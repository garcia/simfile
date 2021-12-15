import abc
import os
import posixpath
from typing import List
import zipfile

from .. import open as simfile_open
from ..types import Simfile


class AbstractFileSystem(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def isfile(self, path: str) -> bool: pass
    @abc.abstractmethod
    def listdir(self, path: str) -> List[str]: pass
    @abc.abstractmethod
    def open_simfile(self, path: str) -> Simfile: pass

    def join(self, path: str, *paths: str) -> str:
        return posixpath.join(path, *paths)


class OSFileSystem(AbstractFileSystem):
    def isfile(self, path: str) -> bool:
        return os.path.isfile(path)
    def listdir(self, path: str) -> List[str]:
        return os.listdir(path)
    def open_simfile(self, path: str) -> Simfile:
        return simfile_open(path)
    def join(self, path: str, *paths: str) -> str:
        return os.path.join(path, *paths)


class ZipFileSystem(AbstractFileSystem):
    def __init__(self, zip_file: zipfile.ZipFile):
        self.zip_file = zip_file
        self.namelist = zip_file.namelist()

    def isfile(self, path: str) -> bool:
        # TODO: validate path is a file and not a directory
        return path in self.namelist
    
    def listdir(self, path: str) -> List[str]:
        raise NotImplementedError # TODO
    
    def open_simfile(self, path: str) -> Simfile:
        raise NotImplementedError # TODO
