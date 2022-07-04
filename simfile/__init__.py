"""
Convenience functions for loading & modifying simfiles.

All functions take a `strict` parameter that defaults to True. By
default, the underlying parser will throw an exception if it finds any
stray text between parameters. This behavior can be overridden by
setting `strict` to False.
"""
from contextlib import contextmanager
from io import StringIO
from itertools import tee
from typing import Iterator, List, Optional, TextIO, Tuple, Union, cast

from fs.base import FS
from msdparser import parse_msd

from simfile._private.nativeosfs import NativeOSFS
from simfile.dir import SimfileDirectory, SimfilePack

from .ssc import SSCSimfile
from .sm import SMSimfile
from .types import Simfile


__version__ = '2.1.0-beta.3'
__all__ = [
    'load', 'loads', 'open', 'open_with_detected_encoding', 'opendir',
    'openpack', 'CancelMutation', 'mutate',
]


ENCODINGS = ['utf-8', 'cp1252', 'cp932', 'cp949']


def _detect_ssc(
    file: Union[TextIO, Iterator[str]],
    strict: bool = True
) -> Tuple[Union[TextIO, Iterator[str]], bool]:
    if isinstance(file, TextIO):
        if type(file.name) is str:
            _, _, suffix = file.name.rpartition('.')
            if suffix == '.ssc':
                return (file, True)
            elif suffix == '.sm':
                return (file, False)
        parser = parse_msd(file=file, ignore_stray_text=not strict)
    else:
        file, peek_file = [StringIO(''.join(f)) for f in tee(file)]
        parser = parse_msd(
            string=''.join(peek_file),
            ignore_stray_text=not strict,
        )

    # Check if the first property is an SSC version
    try:
        first_param = next(parser)
    except StopIteration:
        return (file, False)
    
    if isinstance(file, TextIO):
        file.seek(0)

    return (file, first_param.key is not None and first_param.key.upper() == 'VERSION')


def load(file: Union[TextIO, Iterator[str]], strict: bool = True) -> Simfile:
    """
    Load a text file object as a simfile.

    If the file object has a filename with a matching extension, it
    will be used to infer the correct implementation. Otherwise, the
    first property in the file is peeked at. If its key is "VERSION",
    the file is treated as an SSC simfile; otherwise, it's treated as
    an SM simfile.
    """
    file, is_ssc = _detect_ssc(file)
    if is_ssc:
        return SSCSimfile(file=file, strict=strict)
    else:
        return SMSimfile(file=file, strict=strict)


def loads(string: str, strict: bool = True) -> Simfile:
    """
    Load a string containing simfile data as a simfile.
    """
    return load(StringIO(string), strict=strict)


def open(
    filename: str,
    strict: bool = True,
    filesystem: FS = NativeOSFS(),
    **kwargs
) -> Simfile:
    """
    Load a simfile by filename.

    Keyword arguments are passed to the builtin `open` function.
    If no encoding is specified, this function will defer to
    :func:`open_with_detected_encoding`.
    """
    try_encodings = ENCODINGS
    if 'encoding' in kwargs:
        try_encodings = [kwargs.pop('encoding')]
    
    return open_with_detected_encoding(
        filename,
        try_encodings=try_encodings,
        strict=strict,
        filesystem=filesystem,
        **kwargs
    )[0]


def open_with_detected_encoding(
    filename: str,
    try_encodings: List[str] = ENCODINGS,
    strict: bool = True,
    filesystem: FS = NativeOSFS(),
    **kwargs
) -> Tuple[Simfile, str]:
    """
    Load a simfile by filename; returns the simfile and detected encoding.

    Tries decoding the simfile as UTF-8, CP1252 (English), CP932
    (Japanese), and CP949 (Korean), mirroring the encodings supported
    by StepMania. This list can be overridden by supplying
    `try_encodings`.

    Keep in mind that no heuristics are performed to "guess" the
    correct encoding - this method simply tries each encoding in order
    until one succeeds. As such, non-UTF-8 files may successfully parse
    as the wrong encoding, resulting in garbled text. If you intend to
    write the simfile back to disk, make sure to use the same encoding
    that was detected to preserve the true byte sequence.

    In general, you only need to use this function directly if you need
    to know the file's encoding. :func:`.open` and :func:`.mutate` both
    defer to this function to detect the encoding behind the scenes.
    """
    if 'encoding' in kwargs:
        raise TypeError(
            "unexpected encoding argument - use try_encodings instead"
        )

    exception: Optional[UnicodeDecodeError] = None
    
    for encoding in try_encodings:
        try:
            with filesystem.open(
                filename,
                'r',
                encoding=encoding,
                **kwargs
            ) as file:
                return (load(file, strict=strict), encoding)
        except UnicodeDecodeError as e:
            # Keep track of each encoding's exception
            if exception:
                e.__cause__ = exception
                exception = e
            else:
                exception = e
            continue
    
    # If all encodings failed, raise the exception chain
    raise exception or UnicodeError


def opendir(
    simfile_dir: str,
    filesystem: FS = NativeOSFS(),
    **kwargs
) -> Tuple[Simfile, str]:
    """
    Open a simfile from its directory path; returns the simfile and its path.

    If both SSC and SM are present, SSC is preferred. Keyword arguments
    are passed down to :func:`simfile.open`.
    
    If you need more flexibility (for example, if you need both the SM and
    SSC files), try using :class:`.SimfileDirectory`.
    """
    sd = SimfileDirectory(
        simfile_dir,
        filesystem=filesystem,
    )
    
    return (sd.open(**kwargs), cast(str, sd.ssc_path or sd.sm_path))


def openpack(
    pack_dir: str,
    filesystem: FS = NativeOSFS(),
    **kwargs
) -> Iterator[Tuple[Simfile, str]]:
    """
    Open a pack of simfiles from the pack's directory path;
    yields (simfile, filename) tuples.

    Only immediate subdirectories of :code:`pack_dir` containing an SM or
    SSC file are included. Simfiles aren't guaranteed to appear in any
    particular order. If both SSC and SM are present, SSC is preferred.
    Keyword arguments are passed down to :func:`simfile.open`.
    
    If you need more flexibility (for example, if you need the pack's
    banner or a :class:`.SimfileDirectory` for each simfile), try using
    :class:`.SimfilePack`.
    """
    sp = SimfilePack(pack_dir, filesystem=filesystem)

    yield from (
        (simfile_dir.open(), cast(str, simfile_dir.ssc_path or simfile_dir.sm_path))
        for simfile_dir in sp.simfile_dirs()
    )


class CancelMutation(BaseException):
    """
    Raise from inside a :func:`mutate` block to prevent saving the simfile.
    """


@contextmanager
def mutate(
    input_filename: str,
    output_filename: Optional[str] = None,
    backup_filename: Optional[str] = None,
    try_encodings: List[str] = ENCODINGS,
    strict: bool = True,
    filesystem: FS = NativeOSFS(),
    **kwargs
) -> Iterator[Simfile]:
    """
    Context manager that loads & saves a simfile by filename.

    If an `output_filename` is provided, the modified simfile will be
    written to that filename upon exit from the context manager.
    Otherwise, it will be written back to the `input_filename`.

    If a `backup_filename` is provided, the *original* simfile will be
    written to that filename upon exit from the context manager.
    Otherwise, no backup copy will be written. `backup_filename` must
    be distinct from `input_filename` and `output_filename` if present.

    If the context manager catches an exception, nothing will be
    written to disk, and the exception will be re-thrown. To prevent
    saving without causing the context manager to re-throw an
    exception, raise :class:`CancelMutation`.

    Keyword arguments are passed to the builtin :code:`open` function.
    Uses :func:`open_with_detected_encoding` to detect & preserve the
    encoding. The list of encodings can be overridden by supplying
    `try_encodings`.
    """
    if backup_filename:
        if backup_filename in (input_filename, output_filename):
            raise ValueError(
                'backup_filename must be distinct from input/output filenames'
            )
    
    simfile, encoding = open_with_detected_encoding(
        input_filename,
        try_encodings=try_encodings,
        strict=strict,
        filesystem=filesystem,
        **kwargs
    )

    # Preserve the original simfile contents if a backup file was requested
    backup_data = str(simfile) if backup_filename else ''

    try:
        yield simfile
    except CancelMutation:
        return # Don't re-raise
    except:
        raise
    else:
        # No exception was caught, so write the output file(s)
        
        # Write backup file if requested
        if backup_filename:
            with filesystem.open(
                backup_filename,
                'w',
                encoding=encoding,
                **kwargs
            ) as writer:
                writer.write(backup_data)
        
        # Write output file
        with filesystem.open(
            output_filename or input_filename,
            'w',
            encoding=encoding,
            **kwargs
        ) as writer:
            simfile.serialize(cast(TextIO, writer))