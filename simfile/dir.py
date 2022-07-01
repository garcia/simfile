from typing import Iterator, List, Optional, Tuple

from fs.base import FS

import simfile
from .assets import Assets
from .types import Simfile
from simfile._private.path import FSPath
from ._private import extensions
from ._private.nativeosfs import NativeOSFS


__all__ = ['DuplicateSimfileError', 'SimfileDirectory', 'SimfilePack']


class DuplicateSimfileError(Exception):
    """
    Raised when a simfile directory contains multiple simfiles of the same
    type (e.g. two SM files).
    """


class SimfileDirectory:
    """
    A simfile directory, containing an SM and/or SSC file, or neither.

    Raises :class:`DuplicateSimfileError` if the directory contains
    multiple simfiles of the same type (e.g. two SM files).
    """

    sm_path: Optional[str] = None
    """Absolute path to the SM file, if present."""
    
    ssc_path: Optional[str] = None
    """Absolute path to the SSC file, if present."""

    def __init__(
        self,
        simfile_dir: str,
        *,
        filesystem: FS = NativeOSFS(),
    ):
        self.simfile_dir = simfile_dir
        self.filesystem = filesystem
        self._path = FSPath(filesystem)
        self._dirlist: List[str] = self.filesystem.listdir(simfile_dir)
        
        for simfile_item in self._dirlist:
            match = extensions.match(simfile_item, *extensions.SIMFILE)
            if match:
                simfile_path = self._path.join(simfile_dir, simfile_item)
                if match == '.sm':
                    if self.sm_path:
                        raise DuplicateSimfileError(
                            f"{repr(self.sm_path)}, {repr(simfile_path)}"
                        )
                    self.sm_path = simfile_path
                elif match == '.ssc':
                    if self.ssc_path:
                        raise DuplicateSimfileError(
                            f"{repr(self.ssc_path)}, {repr(simfile_path)}"
                        )
                    self.ssc_path = simfile_path
    
    def open(self, **kwargs) -> Simfile:
        """
        Open the simfile in this directory.
        
        If both SSC and SM are present, SSC is preferred. Keyword arguments
        are passed down to :func:`simfile.open`.

        Raises :code:`FileNotFoundError` if there is no SM or SSC file in
        the directory.
        """
        if 'filesystem' in kwargs:
            raise TypeError(
                "Can't specify filesystem from SimfileDirectory.open "
                "(try specifying it when creating the SimfileDirectory)"
            )
        
        preferred_simfile = self.ssc_path or self.sm_path
        if not preferred_simfile:
            raise FileNotFoundError('no simfile in directory')
        
        return simfile.open(
            preferred_simfile,
            filesystem=self.filesystem,
            **kwargs
        )
    
    def assets(self) -> Assets:
        """
        Get the file assets for this simfile.
        """
        return Assets(self.simfile_dir, simfile=self.open())


class SimfilePack:
    """
    A simfile pack directory, containing any number of simfile directories.

    Only immediate subdirectories of :code:`pack_dir` containing an SM or
    SSC file are included. Simfiles aren't guaranteed to appear in any
    particular order.
    """
    simfile_paths: Tuple[str]
    """Absolute paths to the simfile directories in this pack."""
    
    def __init__(
        self,
        pack_dir: str,
        *,
        filesystem: FS = NativeOSFS(),
    ):
        self.pack_dir = pack_dir
        self.filesystem = filesystem
        self._path = FSPath(filesystem)
        self.simfile_paths = tuple(self._find_simfile_paths())
    
    def _find_simfile_paths(self) -> Iterator[str]:
        for pack_item in self.filesystem.listdir(self.pack_dir):
            simfile_path = self._path.join(self.pack_dir, pack_item)
            if not self.filesystem.isdir(simfile_path):
                continue
            
            # Check whether this directory has any simfiles in it
            for simfile_item in self.filesystem.listdir(simfile_path):
                if extensions.match(simfile_item, *extensions.SIMFILE):
                    yield simfile_path
                    break
    
    def simfile_directories(self) -> Iterator[SimfileDirectory]:
        """
        Iterator over the simfile directories in the pack.
        """
        for simfile_path in self.simfile_paths:
            yield SimfileDirectory(simfile_path, filesystem=self.filesystem)
    
    def simfiles(self, **kwargs) -> Iterator[Simfile]:
        """
        Iterator over the simfiles in the pack.

        If both SSC and SM are present in a simfile directory, SSC is
        preferred. Keyword arguments are passed down to
        :func:`simfile.open`.
        """
        for simfile_dir in self.simfile_directories():
            yield simfile_dir.open(**kwargs)
    
    @property
    def name(self):
        """Get the name of the pack (the directory name by itself)."""
        return self._path.split(self.pack_dir)[1]
    
    def banner(self) -> Optional[str]:
        """
        Get the pack's banner image, if present, as an absolute path.
        """
        for image_type in extensions.IMAGE[::-1]:
            for pack_item in self.filesystem.listdir(self.pack_dir):
                if extensions.match(pack_item, image_type):
                    return self._path.join(self.pack_dir, pack_item)
        
        # No image matches found in the pack directory
        # Check for images alongside the pack directory with the same name
        songs_dir, pack_name = self._path.split(self.pack_dir)
        for image_type in extensions.IMAGE[::-1]:
            parent_banner = self._path.join(songs_dir, pack_name + image_type)
            if self.filesystem.exists(parent_banner):
                return parent_banner