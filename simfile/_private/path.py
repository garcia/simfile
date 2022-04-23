import os

from fs.base import FS
import fs.path

from .nativeosfs import NativeOSFS


__all__ = ['FSPath']


class FSPath:
    def __init__(self, filesystem: FS):
        self.filesystem = filesystem
        
    def normpath(self, path: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.normpath(path)
        else:
            return fs.path.normpath(path)
    
    def join(self, *paths: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.join(*paths)
        else:
            return fs.path.join(*paths)
