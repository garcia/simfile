import os
from typing import Tuple

from fs.base import FS
import fs.path

from .nativeosfs import NativeOSFS


__all__ = ['FSPath']


class FSPath:
    def __init__(self, filesystem: FS):
        self.filesystem = filesystem
    
    def join(self, *paths: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.join(*paths)
        else:
            return fs.path.join(*paths)
    
    def normpath(self, path: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.normpath(path)
        else:
            return fs.path.normpath(path)
    
    def split(self, path: str) -> Tuple[str, str]:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.split(path)
        else:
            return fs.path.split(path)