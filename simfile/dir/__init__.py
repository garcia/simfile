import os
from typing import Iterator, List, Mapping, MutableMapping, NamedTuple, Optional, Sequence

from fs.base import FS
import fs.path

from ._private.nativeosfs import NativeOSFS
from ..types import Simfile
from .. import load as simfile_load


__all__ = ['SimfileDirectory', 'SimfilePack']


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
    @property # type: ignore
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
    @property # type: ignore
    def asset_property(self: 'SimfileDirectory') -> Optional[str]:
        if prop in self._cache: return self._cache[prop]
        
        specified_path = self.simfile.get(prop)
        if specified_path:
            full_path = self._join(self.simfile_dir, specified_path)
            if self.filesystem.isfile(full_path):
                return self._cache_path(prop, specified_path)
        
        asset_definition = ASSET_DEFINITIONS[prop]
        for file_in_simfile_dir in self._dirlist:
            if asset_definition.matches(file_in_simfile_dir):
                return self._cache_path(prop, file_in_simfile_dir)
        
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
    filesystem: FS

    def __init__(
        self,
        simfile_dir: str,
        *,
        simfile: Optional[Simfile] = None,
        filesystem: FS = NativeOSFS(),
    ):
        self.simfile_dir = simfile_dir
        self.filesystem = filesystem
        self._dirlist: List[str] = self.filesystem.listdir(simfile_dir)
        self._cache: MutableMapping[str, Optional[str]] = {}

        self.simfile = simfile or self._open_simfile()
    
    def _open_simfile(self) -> Simfile:
        preferred_simfile = self.ssc or self.sm
        if not preferred_simfile:
            raise FileNotFoundError('no simfile in directory')
        
        return simfile_load(self.filesystem.open(preferred_simfile))
    
    def _normpath(self, path: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.normpath(path)
        else:
            return fs.path.normpath(path)
    
    def _join(self, *paths: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.join(*paths)
        else:
            return fs.path.join(*paths)
    
    def _cache_path(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None:
            self._cache[key] = self._normpath(self._join(self.simfile_dir, value))
        else:
            self._cache[key] = None
        return self._cache[key]


class SimfilePack:
    def __init__(
        self,
        pack_dir: str,
        *,
        filesystem: FS = NativeOSFS(),
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