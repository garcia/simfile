"""
Simfile parser for Python. This library currently only supports the .SM
format; .SSC support is planned for the future.
"""
import codecs
from decimal import Decimal
from fractions import Fraction, gcd as _gcd
import os

__author__ = 'Grant Garcia'
__copyright__ = 'Copyright 2013, Grant Garcia'
__license__ = 'MIT'
__version__ = '0.6.2'

__all__ = ['MultiInstanceError', 'Param', 'Notes', 'Chart', 'Timing', 'Simfile']

# Used internally

def enum(*sequential, **named):
    """Create an enum out of both sequential and named elements."""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def gcd(*numbers):
    """Return the greatest common divisor of the given integers"""
    return reduce(_gcd, numbers)

def lcm(*numbers):
    """Return lowest common multiple."""    
    def lcm(a, b):
        return (a * b) // gcd(a, b)
    return reduce(lcm, numbers, 1)

def decimal_to_192nd(dec):
    """Convert a decimal value to a fraction whose denominator is 192."""
    return Fraction(int(round(Decimal(dec) * 192)), 192)

def decimal_from_192nd(frac):
    """Convert a fraction to a decimal value quantized to 1/1000."""
    return Decimal(float(frac)).quantize(Decimal('0.001'))

# Special exceptions
class MultiInstanceError(Exception):
    """
    Raised upon attempting to retrieve a parameter or chart for which there
    are multiple possible return values.

    This can always be resolved by setting the 'index' argument to 0.
    """


class Param(list):
    """
    Represents a parameter as a list of values.

    This class is identical to `list` but includes a special __str__ method.
    """
    def __str__(self):
        return ('#' + ':'.join(str(elem) for elem in self) + ';')

    def __repr__(self):
        return '%s(%s)' % ('Param', super(Param, self).__repr__())


class Notes(object):
    """
    Encapsulates note data.

    The sole constructor argument should be a string of .SM note data. See
    `the StepMania wiki <http://www.stepmania.com/wiki/The_.SM_file_format>`_
    for more details.
    """
    def _sort(self):
        if self._out_of_order:
            self.notes.sort(key=lambda x: x[0])

    def _clean_line(self, line):
        # Remove unnecessary whitespace
        line = line.strip()
        # Remove comments
        if line.find('//') >= 0:
            line = line.split('//', '1')[0]
        # The line may be empty; use filter(None, ...) to account for this
        return line

    def __init__(self, notedata=None):
        self.notes = []
        self.arrows = None
        self._out_of_order = False

        if not notedata:
            return

        # Iterate over measures
        # TODO: skip commas within comments
        for m, measuredata in enumerate(notedata.split(',')):
            measure_lines = filter(None,
                (self._clean_line(line) for line in measuredata.splitlines()))
            measure_len = len(measure_lines)
            # Iterate over lines of measure
            for l, line in enumerate(measure_lines):
                # Set the number of arrows to the first line's length
                if self.arrows is None:
                    self.arrows = len(line)
                # Ignore blank lines (e.g. "0000")
                if any(a != '0' for a in line):
                    line_pos = (m + Fraction(l, measure_len)) * 4
                    self.notes.append([line_pos, line])

    def get_region(self, start, end, inclusive=False, _pop=False):
        """Gets the region at the given endpoints."""
        if start > end:
            raise ValueError("start > end")
        # If we're actually retrieving a region, sort the notes first
        elif start < end:
            self._sort()
        rtn = Notes()
        rtn.arrows = self.arrows
        # pop_region: iterate over a copy of the note data
        if _pop:
            notes = self.notes[:]
            _pop_offset = 0
        else:
            notes = self.notes
        # Search for and remove the existing rows if possible
        for r, row in enumerate(notes):
            if ((inclusive and start <= row[0] <= end) or
                    (not inclusive and start <= row[0] < end)):
                rtn.notes.append((row[0] - start, row[1]))
                # pop_region: pop the row afterward
                if _pop:
                    self.notes.pop(r - _pop_offset)
                    _pop_offset += 1
            # If we're retrieving a single row, this will trivially be true.
            # Otherwise, the data must be sorted, so when we've reached the end
            # we can be sure that there are no more rows to locate.
            if row[0] >= end:
                return rtn
        # Return if we haven't already returned
        return rtn

    def pop_region(self, start, end, inclusive=False):
        """Gets and clears the region at the given endpoints."""
        return self.get_region(start, end, inclusive, _pop=True)

    def set_region(self, start, end, notes, inclusive=False):
        """Sets the region at the given endpoints to the given note data."""
        # If we're setting the region to itself, make a copy first, otherwise
        # it might end up infinitely looping
        if notes is self:
            notes = Notes(unicode(notes))
        # Start by clearing the region
        # This doubles as a "start > end" check
        self.pop_region(start, end, inclusive)
        # Set _out_of_order now instead of after the for-loop, just in case
        # something goes awry halfway through it
        self._out_of_order = True
        # Insert the note data
        for r, row in enumerate(notes.notes):
            if ((inclusive and row[0] <= end - start) or
                    (not inclusive and row[0] < end - start)):
                self.notes.append((row[0] + start, row[1]))

    def get_row(self, pos):
        """Gets the row at the given position."""
        return self.get_region(start=pos, end=pos, inclusive=True)

    def pop_row(self, pos):
        """Gets and clears the row at the given position."""
        return self.pop_region(start=pos, end=pos, inclusive=True)

    def set_row(self, pos, notes):
        """Sets the row at the given position to the given note data."""
        return self.set_region(start=pos, end=pos, notes=notes, inclusive=True)

    def _measure_to_str(self, m, measure):
        rtn = []
        rows = lcm(*[r[0].denominator for r in measure])
        for r in [(m * 4 + Fraction(n, rows)) for n in xrange(rows * 4)]:
            if measure and measure[0][0] == r:
                rtn.append(measure.pop(0)[1])
            else:
                rtn.append('0' * self.arrows)
        return rtn

    def __str__(self):
        self._sort()
        rtn = []
        measure = []
        m = 0
        for row in self.notes:
            # Usually this will only get executed once at a time, but if
            # there's an empty measure it'll execute twice or more
            while row[0] / 4 >= m + 1:
                rtn.extend(self._measure_to_str(m, measure))
                rtn.append(',')
                measure = []
                m += 1
            measure.append(row)
        rtn.extend(self._measure_to_str(m, measure))
        return '\n'.join(rtn)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Chart(object):
    """
    Encapsulates chart data.

    The sole constructor argument should be a list of parameter values,
    usually returned by Simfile.get_raw_chart.

    Exposes attributes 'stepstype', 'description', 'difficulty', and 'radar'
    as strings, 'meter' as an integer, and 'notes' as a Notes object.
    """
    def __init__(self, chart):
        if (chart[0] != 'NOTES'):
            raise ValueError('Not a chart')

        self.stepstype = chart[1]
        self.description = chart[2]
        self.difficulty = chart[3]
        self.meter = int(chart[4])
        self.radar = chart[5]
        self.notes = Notes(chart[6])

    def __str__(self):
        return ('#NOTES:\n'
                '     {stepstype}:\n'
                '     {description}:\n'
                '     {difficulty}:\n'
                '     {meter}:\n'
                '     {radar}:\n'
                '{notes}\n;\n').format(
                    stepstype=self.stepstype,
                    description=self.description,
                    difficulty=self.difficulty,
                    meter=self.meter,
                    radar=self.radar,
                    notes=self.notes)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Timing(list):
    """
    Encapsulate timing data as a list of [beat, value] lists.

    The sole constructor argument should be a string of BPM or stop values.
    """
    def __init__(self, tdata):
        tlist = []
        for tline in tdata.split(','):
            t = tline.strip().split('=')
            if ''.join(t):
                tlist.append([decimal_to_192nd(t[0]), Decimal(t[1])])
        self.extend(tlist)

    def __str__(self):
        return ',\n'.join(
            '='.join((str(decimal_from_192nd(t[0])), str(t[1])))
            for t in self)

    def __repr__(self):
        return '%s(%s)' % ('Timing', super(Timing, self).__repr__())


class Simfile(object):
    """
    Encapsulates simfile data.

    The sole constructor argument should be a path to a valid .SM file.
    """
    DEFAULT_RADAR = u'0,0,0,0,0'
    states = enum('NEXT_PARAM', 'READ_VALUE', 'COMMENT')
    filename = dirname = None

    def __init__(self, filename=None, string=None):
        """
        Parse the given simfile.

        If the 'filename' argument is given, reads a simfile from the given
        file. If the 'string' argument is given, parses the string instead.
        Passing both arguments is disallowed.

        The functionality of this code should mirror StepMania's
        MsdFile.cpp fairly closely.
        """
        if filename:
            if string:
                raise TypeError('Simfile() takes either a filename '
                                'or a string -- not both')
            self.filename = filename
            self.dirname = os.path.dirname(filename)
            with codecs.open(filename, encoding='utf-8') as simfile_h:
                string = simfile_h.read()

        state = self.states.NEXT_PARAM
        params = []
        i = 0
        for i, c in enumerate(string):
            # Start of comment
            if i + 1 < len(string) and c == '/' and string[i + 1] == '/':
                old_state = state
                state = self.states.COMMENT
            # Comment
            elif state == self.states.COMMENT:
                if c in '\r\n':
                    state = old_state
                    continue
            # Start of parameter
            if state == self.states.NEXT_PARAM:
                if c == '#':
                    state = self.states.READ_VALUE
                    param = ['']
            # Read value
            elif state == self.states.READ_VALUE:
                # Fix missing semicolon
                if c == '#' and string[i - 1] in '\r\n':
                    param[-1] = param[-1].strip()
                    params.append(self._wrap(param))
                    param = ['']
                # Next value
                elif c == ':':
                    param[-1] = param[-1].strip()
                    param.append('')
                # Next parameter
                elif c == ';':
                    param[-1] = param[-1].strip()
                    params.append(self._wrap(param))
                    state = self.states.NEXT_PARAM
                # Add character to param
                else:
                    param[-1] += c
        # Add partial parameter (i.e. if the last one was missing a semicolon)
        if state == self.states.READ_VALUE:
            params.append(self._wrap(param))

        self.params = params

    def _wrap(self, param):
        if param[0].upper() == 'NOTES':
            return Chart(param)
        elif param[0].upper() in ('BPMS', 'STOPS'):
            return Param((param[0], Timing(param[1])))
        else:
            return Param(param)

    def get(self, identifier):
        """
        Retrieve the value(s) denoted by (and including) the identifier as a
        Parameter object.

        Raises KeyError if there is no such identifier and MultiInstanceError
        if multiple parameters begin with the identifier, or if it is known to
        be a multi-instance identifier (i.e. NOTES).

        Identifiers are case-insensitive, but their "true" case can be
        determined by the observing the first element of the parameter.
        """
        identifier = identifier.upper()
        if identifier == 'NOTES':
            raise MultiInstanceError('Use get_chart to retrieve charts')
        found_param = None
        for param in self.params:
            # Skip charts
            if type(param) is not Param:
                continue
            if param[0].upper() == identifier:
                if found_param:
                    raise MultiInstanceError('Multiple instances of identifier')
                found_param = param
        if found_param:
            return found_param
        else:
            raise KeyError('No such identifier')

    def get_string(self, identifier):
        """Retrieve the data following the identifier as a single string."""
        return ":".join(self.get(identifier)[1:])

    def set(self, identifier, *values):
        """
        Sets the identifier to the given value(s).

        This creates a new parameter if the identifier cannot be found in the
        simfile. Otherwise, it modifies the existing parameter.
        """
        # If the identifier already exists, edit it
        try:
            param = self.get(identifier)
        # Otherwise, create a new one
        except KeyError:
            param = Param([unicode(identifier), u''])
        param[1:] = [unicode(v) for v in values]
        # Add the parameter if it was just created
        if param not in self.params:
            self.params.append(param)

    def get_chart(self, difficulty=None, stepstype=None, meter=None,
                  description=None, index=None):
        """
        Retrieve the specified chart.

        'difficulty', 'stepstype', 'meter', and/or 'description' can all be
        specified to narrow a search for a specific chart. If the 'index'
        parameter is omitted, there must be exactly one chart that fits the
        given parameters. Otherwise, the index-th matching chart is returned.

        Raises MultiInstanceError in ambiguous cases, KeyError if no chart
        matched the given parameters, and IndexError if an invalid index was
        given. Otherwise the chart's values are returned as a dictionary.
        """
        found_chart = None
        if index != None:
            i = 0
        for chart in filter(lambda p: type(p) is Chart, self.params):
            # Check parameters
            if ((difficulty and not chart.difficulty == difficulty or
                 stepstype and not chart.stepstype == stepstype or
                 meter and not chart.meter == meter or
                 description and not chart.description == description) and
                 any((difficulty, stepstype, meter, description))):
                continue
            # Already found a chart that fits the parameters
            if found_chart and index == None:
                hint = 'which index'
                if found_chart.stepstype != chart.stepstype:
                    hint = 'which stepstype'
                elif found_chart.meter != int(chart.meter):
                    hint = 'which meter'
                elif found_chart.description != chart.description:
                    hint = 'which description'
                raise MultiInstanceError('Ambiguous parameters (%s?)' % hint)
            found_chart = chart
            if index != None:
                if i == index:
                    return found_chart
                i += 1
        if not found_chart or index != None and i == 0:
            raise KeyError('No charts fit the given parameters')
        if index != None:
            raise IndexError('Only %s charts fit the given parameters' % i)
        return found_chart

    def set_chart(self, notes, difficulty=None, stepstype=None, meter=None,
                  description=None, index=None, radar=None):
        """
        Change a chart from or add a chart to the simfile.

        The arguments are identical to those of get_chart, with the exception
        of the required 'notes' argument at the beginning and the optional
        'radar' argument at the end. The 'stepstype' argument is required when
        adding a new chart, but not when editing an existing chart (assuming
        the other given parameters are sufficiently unambiguous). The 'radar'
        argument is only used when adding a chart.

        Raises any error that get_chart might raise, except for KeyError. Also
        raises ValueError if 'stepstype' is not specified when adding a new
        chart.
        """
        try:
            chart = self.get_chart(difficulty, stepstype, meter, description,
                                   index)
        except KeyError:
            if not stepstype:
                raise ValueError("Must specify stepstype when adding a chart")
            chart = Chart([
                'NOTES',
                stepstype,
                unicode(description) if description else u'synctools',
                unicode(difficulty) if difficulty else u'Edit',
                unicode(meter) if meter else u'1',
                unicode(radar) if radar else self.DEFAULT_RADAR,
                u''
            ])
        chart.notes = notes
        if chart not in self.params:
            self.params.append(chart)

    def save(self, filename=None):
        """
        Writes the simfile to disk.

        If the 'filename' argument is given, it is used. If omitted, the
        simfile will be written to the file from which it was originally read,
        or a ValueError will be raised if it was read from a string.
        """
        filename = filename or self.filename
        if not filename:
            raise ValueError('no filename provided')
        with codecs.open(filename, 'w', 'utf-8') as output:
            output.write(unicode(self))

    def __str__(self):
        return '\n'.join(unicode(param) for param in self.params)

    def __eq__(self, other):
        """
        Test for equality with another Simfile.

        This only compares the parameter lists, not the filenames or any other
        Simfile object attributes.
        """
        return type(self) is type(other) and self.params == other.params