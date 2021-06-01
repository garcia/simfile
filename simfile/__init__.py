import builtins
from contextlib import contextmanager
from io import StringIO
from typing import Iterator, List, Optional, TextIO, Tuple, Union

from msdparser import MSDParser

from .ssc import SSCSimfile
from .sm import SMSimfile
from .types import Simfile
from ._private.tee_file import tee_file


__version__ = '2.0.0-beta.3'
__all__ = [
    'load', 'loads', 'open', 'open_with_detected_encoding', 'CancelMutation',
    'mutate',
]


ENCODINGS = ['utf-8', 'cp1252', 'cp932', 'cp949']


def _detect_ssc(peek_file: Union[TextIO, Iterator[str]]) -> bool:
    if isinstance(peek_file, TextIO) and type(peek_file.name) is str:
        _, _, suffix = peek_file.name.rpartition('.')
        if suffix == '.ssc':
            return True
        elif suffix == '.sm':
            return False

    # Peek at the first property next
    parser = MSDParser(file=peek_file)
    first_key = ''
    for first_key, _ in parser:
        break

    # Check for .SSC version header next
    return first_key.upper() == 'VERSION'


def load(file: Union[TextIO, Iterator[str]]) -> Simfile:
    """
    Load a text file object as a simfile using the correct implementation.

    If the file object has a filename with a matching extension, it
    will be used to infer the correct implementation. Otherwise, the
    first property in the file is peeked at. If its key is "VERSION",
    the file is treated as an SSC simfile; otherwise, it's treated as
    an SM simfile.
    """
    peek_file, file = tee_file(file)
    is_ssc = _detect_ssc(peek_file)
    return SSCSimfile(file=file) if is_ssc else SMSimfile(file=file)


def loads(string: str = None) -> Simfile:
    """
    Load a string as a simfile using the correct implementation.
    """
    return load(StringIO(string))


def open(filename: str, **kwargs) -> Simfile:
    """
    Load a simfile by filename using the correct implementation.

    Keyword arguments are passed to the builtin `open` function.
    If no encoding is specified, this function will defer to
    :func:`open_with_detected_encoding`.
    """
    try_encodings = ENCODINGS
    if 'encoding' in kwargs:
        try_encodings = [kwargs.pop('encoding')]
    
    return open_with_detected_encoding(
        filename,
        try_encodings,
        **kwargs
    )[0]


def open_with_detected_encoding(
    filename: str,
    try_encodings: List[str] = ENCODINGS,
    **kwargs
) -> Tuple[Simfile, str]:
    """
    Load a simfile by filename using the correct implementation & encoding.

    Tries decoding the simfile as UTF-8, CP1252 (English), CP932
    (Japanese), and CP949 (Korean), mirroring the encodings supported
    by StepMania. This list can be overridden by supplying `try_encodings`.
    """
    if 'encoding' in kwargs:
        raise TypeError(
            "unexpected encoding argument - use try_encodings instead"
        )

    exception: Optional[UnicodeDecodeError] = None
    
    for encoding in try_encodings:
        try:
            with builtins.open(
                filename,
                'r',
                encoding=encoding,
                **kwargs
            ) as file:
                return (load(file), encoding)
        except UnicodeDecodeError as e:
            # Keep track of each encoding's exception
            if exception:
                e.__cause__ = exception
                exception = e
            else:
                exception = e
            continue
    
    # If all encodings failed, raise the exception chain
    raise exception or UnicodeDecodeError


class CancelMutation(BaseException):
    """
    Raise from inside a :func:`mutate` block to prevent saving the simfile.
    """


@contextmanager
def mutate(
    filename: str,
    try_encodings: List[str] = ENCODINGS,
    **kwargs
) -> Iterator[Simfile]:
    """
    Context manager that loads & saves a simfile by filename.

    The simfile is saved upon exit unless the context manager catches
    an exception. To prevent saving without causing the context manager
    to re-throw an exception, raise CancelMutation.

    Keyword arguments are passed to the builtin `open` function.
    Uses :func:`open_with_detected_encoding` to detect & preserve the
    encoding. The list of encodings can be overridden by supplying
    `try_encodings`.
    """
    simfile, encoding = open_with_detected_encoding(
        filename,
        try_encodings,
        **kwargs
    )
    try:
        yield simfile
    except CancelMutation:
        return
    except:
        raise
    else:
        with builtins.open(
            filename,
            'w',
            encoding=encoding,
            **kwargs
        ) as writer:
            simfile.serialize(writer)