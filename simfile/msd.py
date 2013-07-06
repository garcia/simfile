from __future__ import with_statement, unicode_literals
import codecs
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ['MSDParser']

NEXT_PARAM, READ_VALUE, COMMENT = xrange(3)

def _encode_value(value):
    return value.getvalue().strip().decode('utf-8')

def MSDParser(infile):
    # Determine encoding, or default to UTF-8
    encoding = 'utf-8'
    if hasattr(infile, 'encoding') and infile.encoding:
        encoding = infile.encoding
    # Initialization
    state = NEXT_PARAM
    param = []
    value = StringIO()
    i = 0
    # Convert strings into objects that behave like files when iterated over
    if isinstance(infile, basestring):
        infile = infile.splitlines(True)
    for line in infile:
        for i, c in enumerate(line):
            # This is the most frequent scenario, so it sits at the front of
            # the loop for optimization purposes.
            if state == READ_VALUE and c not in '#:;/':
                value.write(c.encode(encoding))
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
                    param.append(_encode_value(value))
                    yield param
                    param = []
                    value = StringIO()
                # Next value
                elif c == ':':
                    param.append(_encode_value(value))
                    value = StringIO()
                # Next parameter
                elif c == ';':
                    param.append(_encode_value(value))
                    yield param
                    param = []
                    value = StringIO()
                    state = NEXT_PARAM
                else:
                    value.write(c)
    # Add partial parameter (i.e. if the last one was missing a semicolon)
    if state == READ_VALUE:
        param.append(_encode_value(value))
        yield param