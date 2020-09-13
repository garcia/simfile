from itertools import tee
from typing import Iterator, TextIO, Union


__all__ = ['TeeFile', 'tee_file']


class TeeFile():
    def __init__(self, file: Union[TextIO, Iterator[str]]):
        self._file = file
    
    def __getattr__(self, name):
        return getattr(self._file, name)
    
    def __iter__(self):
        return iter(self._file)
    
    def __next__(self):
        return next(self._file)

    def close(self):
        pass


def tee_file(file, **kwargs):
    return tuple(TeeFile(tf) for tf in tee(file, **kwargs))
