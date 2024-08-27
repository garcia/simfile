import os
from typing import Tuple

try:
    import fs.path
except ImportError:
    fs = None

from .fs import FS, NativeOSFS


__all__ = ["FSPath"]


class FSPath:
    def __init__(self, filesystem: FS):
        self.filesystem = filesystem

    def join(self, *paths: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.join(*paths)
        else:
            assert fs, "`fs` module is not installed"
            return fs.path.join(*paths)

    def normpath(self, path: str) -> str:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.normpath(path)
        else:
            assert fs, "`fs` module is not installed"
            return fs.path.normpath(path)

    def split(self, path: str) -> Tuple[str, str]:
        if isinstance(self.filesystem, NativeOSFS):
            return os.path.split(path)
        else:
            assert fs, "`fs` module is not installed"
            return fs.path.split(path)
