from io import FileIO, StringIO, TextIOWrapper
from itertools import tee
from typing import cast, Iterator, TextIO, Tuple, TypeVar, Union

from msdparser import MSDParser
from .ssc import SSCSimfile
from .sm import SMSimfile
from ._tee_file import tee_file


__all__ = ['load', 'loads', 'open']


builtin_open = open
AnySimfile = Union[SSCSimfile, SMSimfile]


def load(file: Union[TextIO, Iterator[str]]) -> AnySimfile:
    """
    Load a text file object as a simfile using the correct implementation.

    If the file object has a filename with a matching extension, it will be
    used to infer the correct implementation. Otherwise, the first property
    in the file is peeked at. If the first property key is "VERSION", the
    file is treated as an SSC file; otherwise, it's treated as an SM file.
    """
    
    # Check for filename hint first
    if isinstance(file, TextIO) and type(file.name) is str:
        _, _, suffix = file.name.rpartition('.')
        if suffix == '.ssc':
            return SSCSimfile(file=file)
        elif suffix == '.sm':
            return SMSimfile(file=file)    

    # 
    peek, file = tee_file(file)

    # Default first_key to a string so we can easily fall back to SMSimfile
    parser = MSDParser(file=peek)
    first_key = ''
    for first_key, _ in parser:
        break

    # Check for .SSC version header next
    if first_key.upper() == 'VERSION':
        return SSCSimfile(file=file)
    else:
        return SMSimfile(file=file)


def loads(string: str = None) -> AnySimfile:
    return load(StringIO(string))


def open(filename: str, encoding: str = 'utf-8', **kwargs) -> AnySimfile:
    return load(builtin_open(filename, 'r', encoding=encoding, **kwargs))

