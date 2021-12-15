import os
from typing import Iterator, List, Mapping, MutableMapping, NamedTuple, Optional, Sequence

from . import fs
from ..types import Simfile


__all__ = ['AssetFinder']


SIMFILE_EXTENSIONS = ['.sm', '.ssc']
IMAGE_EXTENSIONS = ['.bmp', '.gif', '.jpeg', '.jpg', '.png']
AUDIO_EXTENSIONS = ['.mp3', '.oga', '.ogg', '.wav']


class AssetDefinition(NamedTuple):
    presets: Sequence[str] = ()
    extensions: Sequence[str] = ()
    match_by_extension: bool = False

    def matches(self, path: str) -> bool:
        ext_match = any(path.lower().endswith(ext) for ext in self.extensions)
        return (
            any(preset in path for preset in self.presets)
            or ext_match and self.match_by_extension
        )


ASSET_DEFINITIONS: Mapping[str, AssetDefinition] = {
    'BANNER': AssetDefinition(
        extensions=IMAGE_EXTENSIONS,
        presets=['bn', 'banner'],
    ),
    'BACKGROUND': AssetDefinition(
        extensions=IMAGE_EXTENSIONS,
        presets=['bg', 'background'],
    ),
    'CDTITLE': AssetDefinition(
        extensions=IMAGE_EXTENSIONS,
        presets=['cdtitle'],
    ),
    'JACKET': AssetDefinition(
        extensions=IMAGE_EXTENSIONS,
        presets=['jk_', 'jacket', 'albumart'],
    ),
    'CDIMAGE': AssetDefinition(
        extensions=IMAGE_EXTENSIONS,
        presets=['-cd'],
    ),
    'DISC': AssetDefinition(
        extensions=IMAGE_EXTENSIONS,
        presets=[' disc', ' title'],
    ),
    'MUSIC': AssetDefinition(
        extensions=AUDIO_EXTENSIONS,
        match_by_extension=True,
    ),
}


def _ext_property(ext: str):
    @property
    def ext_property(self: 'SimfileDirectory') -> Optional[str]:
        # `self.simfile` may be None because these properties are used to find
        # the simfile during AssetFinder initialization (if none was provided)
        if ext in self._cache: return self._cache[ext]

        for asset_path in self._dirlist:
            if asset_path.lower().endswith(ext):
                return self._cache_path(ext, asset_path)
        
        return self._cache_path(ext, None)
    
    return ext_property

def _asset_property(prop: str):
    @property
    def asset_property(self: 'SimfileDirectory') -> Optional[str]:
        if prop in self._cache: return self._cache[prop]
        
        predefined_path = self.simfile.get(prop)
        if predefined_path and self.filesystem.isfile(predefined_path):
            return self._cache_path(prop, predefined_path)
        
        asset_def = ASSET_DEFINITIONS[prop]
        for asset_path in self._dirlist:
            if asset_def.matches(asset_path):
                return self._cache_path(prop, asset_path)
        
        return self._cache_path(prop, None)

    return asset_property


class SimfileDirectory:
    sm = _ext_property('.sm')
    ssc = _ext_property('.ssc')
    music = _asset_property('MUSIC')
    banner = _asset_property('BANNER')
    background = _asset_property('BACKGROUND')
    cdtitle = _asset_property('CDTITLE')
    jacket = _asset_property('JACKET')
    cdimage = _asset_property('CDIMAGE')
    disc = _asset_property('DISC')

    simfile_dir: str
    simfile: Simfile
    filesystem: fs.AbstractFileSystem

    _dirlist: List[str]
    _cache: MutableMapping[str, Optional[str]]

    def __init__(
        self,
        simfile_dir: str,
        *,
        simfile: Optional[Simfile] = None,
        filesystem: fs.AbstractFileSystem = fs.OSFileSystem(),
    ):
        self.simfile_dir = simfile_dir
        self.filesystem = filesystem
        self._dirlist = self.filesystem.listdir(simfile_dir)
        self._cache: MutableMapping[str, str] = {}

        self.simfile = simfile or self._open_simfile()
    
    def _open_simfile(self) -> Simfile:
        ssc = self.ssc
        if ssc: return self.filesystem.open_simfile(ssc)

        sm = self.sm
        if sm: return self.filesystem.open_simfile(sm)
        
        raise FileNotFoundError('no simfile in directory')
    
    def _cache_path(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None:
            self._cache[key] = os.path.normpath(
                os.path.join(self.simfile_dir, value)
            )
        else:
            self._cache[key] = None
        return self._cache[key]


class SimfilePack:
    def __init__(
        self,
        pack_dir: str,
        *,
        filesystem: fs.AbstractFileSystem = fs.OSFileSystem(),
    ):
        self.pack_dir = pack_dir
        self.filesystem = filesystem
    
    def simfile_paths(self) -> Iterator[str]:
        for simfile_path in self.filesystem.listdir(self.pack_dir):
            for asset_path in self.filesystem.listdir(simfile_path):
                if any(asset_path.lower().endswith(ext) for ext in SIMFILE_EXTENSIONS):
                    yield simfile_path
                    break
    
    def simfile_directories(self) -> Iterator[SimfileDirectory]:
        for simfile_path in self.simfile_paths():
            yield SimfileDirectory(simfile_path)
    
    def simfiles(self) -> Iterator[Simfile]:
        for simfile_dir in self.simfile_directories():
            yield simfile_dir.simfile