import builtins
from contextlib import contextmanager
from io import FileIO, StringIO, TextIOWrapper
from itertools import tee
from typing import cast, Iterator, TextIO, Tuple, TypeVar, Union

from msdparser import MSDParser
from .ssc import SSCSimfile
from .sm import SMSimfile
from ._private.tee_file import tee_file


__all__ = ['load', 'loads', 'open', 'CancelMutation', 'mutate']


AnySimfile = Union[SSCSimfile, SMSimfile]


def _open_args(kwargs):
    open_args = {'encoding': 'utf-8'}
    open_args.update(kwargs)
    return open_args


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

    # Split file into two streams for peeking
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
    """
    Load a string as a simfile using the correct implementation.
    """
    return load(StringIO(string))


def open(filename: str, **kwargs) -> AnySimfile:
    """
    Load a simfile from the given filename using the correct implementation.

    Keyword arguments are passed to the builtin `open` function. Encoding
    default to UTF-8.
    """
    return load(builtins.open(filename, 'r', **_open_args(kwargs)))


class CancelMutation(BaseException):
    pass


@contextmanager
def mutate(filename: str, **kwargs):
    """
    Context manager that loads a simfile by filename on entry, then saves
    it to the disk on exit.

    To abort the mutation without causing the context manager to re-throw
    an exception, raise CancelMutation.
    """
    simfile = open(filename, **kwargs)
    try:
        yield simfile
    except CancelMutation:
        return
    except:
        raise
    else:
        with builtins.open(filename, 'w', **_open_args(kwargs)) as writer:
            simfile.serialize(writer)