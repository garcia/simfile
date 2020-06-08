import codecs
from io import StringIO

__all__ = ['MSDParser']

NEXT_PARAM, READ_VALUE, COMMENT = range(3)


class MSDParser(object):
    """
    Parser for MSD files.

    The sole constructor argument should be a file-like object or a string
    containing MSD data. Iterating over an instance yields each parameter as a
    list of strings. The class also implements context management, e.g.
    ``with MSDParser(file) as parser:``; the file will be closed upon
    completion of the block.

    MSDFile should be used instead of Simfile in situations where the chart
    data is not needed, as parsing can be halted before the charts are read in.

    The parser is based off of StepMania's `MsdFile.cpp
    <https://github.com/stepmania/stepmania/blob/master/src/MsdFile.cpp>`_.
    """

    def __init__(self, infile):
        self.infile = infile

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if hasattr(self.infile, 'close'):
            self.infile.close()

    def __iter__(self):
        # Quick access to speed up innermost loop
        infile = self.infile
        # Initialization
        state = NEXT_PARAM
        param = []
        value = StringIO()
        i = 0
        # Convert strings into objects that behave like files upon iteration
        if isinstance(infile, str):
            infile = infile.splitlines(True)
        for line in infile:
            for i, c in enumerate(line):
                # This is the most frequent scenario, so it sits at the front
                # of the loop for optimization purposes.
                if state == READ_VALUE and c not in '#:;/':
                    value.write(c)
                    continue
                # Start of comment
                if c == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    old_state = state
                    state = COMMENT
                # Comment
                elif state == COMMENT:
                    if c in '\r\n':
                        state = old_state
                        continue
                # Start of parameter
                if state == NEXT_PARAM:
                    if c == '#':
                        state = READ_VALUE
                # Read value
                elif state == READ_VALUE:
                    # Fix missing semicolon
                    if c == '#' and i == 0:
                        param.append(value.getvalue())
                        yield param
                        param = []
                        value = StringIO()
                    # Next value
                    elif c == ':':
                        param.append(value.getvalue())
                        value = StringIO()
                    # Next parameter
                    elif c == ';':
                        param.append(value.getvalue())
                        yield param
                        param = []
                        value = StringIO()
                        state = NEXT_PARAM
                    # Only reached if c == '/' and isn't part of a comment;
                    # no need to encode.
                    else:
                        value.write(c)
        # Add partial parameter (i.e. if the last one was missing a semicolon)
        if state == READ_VALUE:
            param.append(value.getvalue())
            yield param
