from __future__ import with_statement, unicode_literals
import codecs
from cStringIO import StringIO
from decimal import Decimal
from fractions import Fraction, gcd
import os
try:
    from collections import OrderedDict
except ImportError:
    # For Python versions < 2.7
    from ordereddict import OrderedDict

from msd import MSDParser


__all__ = ['decimal_to_192nd', 'decimal_from_192nd', 'Notes', 'Chart',
           'Charts', 'Timing', 'Simfile']


def _gcd(*numbers):
    return reduce(gcd, numbers)


def _lcm(*numbers):
    def lcm(a, b):
        return (a * b) // _gcd(a, b)
    return reduce(lcm, numbers, 1)


def decimal_to_192nd(dec):
    """
    Convert a decimal value to a fraction whose denominator is 192.
    """
    return Fraction(int(round(Decimal(dec) * 192)), 192)


def decimal_from_192nd(frac):
    """
    Convert a fraction to a decimal value quantized to 1/1000.
    """
    return Decimal(float(frac)).quantize(Decimal('0.001'))


class SimfileList(list):
    """
    Subclass of 'list' that overrides __repr__.
    """
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           super(SimfileList, self).__repr__())


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
    
    def _get_or_pop_region(self, start, end, inclusive, pop):
        if start > end:
            raise ValueError("start > end")
        # If we're actually retrieving a region, sort the notes first
        elif start < end:
            self._sort()
        rtn = Notes()
        rtn.arrows = self.arrows
        # pop_region: iterate over a copy of the note data
        if pop:
            notes = self.notes[:]
            pop_offset = 0
        else:
            notes = self.notes
        # Search for and remove the existing rows if possible
        for r, row in enumerate(notes):
            if ((inclusive and start <= row[0] <= end) or
                    (not inclusive and start <= row[0] < end)):
                rtn.notes.append((row[0] - start, row[1]))
                # pop_region: pop the row afterward
                if pop:
                    self.notes.pop(r - _pop_offset)
                    pop_offset += 1
            # If we're retrieving a single row, this will trivially be true.
            # Otherwise, the data must be sorted, so when we've reached the end
            # we can be sure that there are no more rows to locate.
            if row[0] >= end:
                return rtn
        # Return if we haven't already returned
        return rtn

    def get_region(self, start, end, inclusive=False):
        """
        Get the region at the given endpoints.
        """
        return self._get_or_pop_region(start, end, inclusive, False)

    def pop_region(self, start, end, inclusive=False):
        """
        Get and clear the region at the given endpoints.
        """
        return self._get_or_pop_region(start, end, inclusive, True)

    def set_region(self, start, end, notes, inclusive=False):
        """
        Set the region at the given endpoints to the given note data.
        """
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
        for row in notes.notes:
            if ((inclusive and row[0] <= end - start) or
                    (not inclusive and row[0] < end - start)):
                self.notes.append((row[0] + start, row[1]))

    def get_row(self, pos):
        """
        Get the row at the given position.
        """
        return self.get_region(start=pos, end=pos, inclusive=True)
    
    def get_row_string(self, pos):
        """
        Get the row at the given position as a one-line string.
        
        This is not the same as str(notes.get_row()), which returns
        a four-line measure padded with zeros.
        """
        row = self.get_row(pos).notes
        if row:
            return row[0][1]
        else:
            return '0' * self.arrows

    def pop_row(self, pos):
        """
        Get and clear the row at the given position.
        """
        return self.pop_region(start=pos, end=pos, inclusive=True)
    
    def pop_row_string(self, pos):
        """
        Get and clear the row at the given position as a one-line string.
        
        This is not the same as str(notes.pop_row()), which returns
        a four-line measure padded with zeros.
        """
        row = self.pop_row(pos).notes
        if row:
            return row[0][1]
        else:
            return '0' * self.arrows

    def set_row(self, pos, notes):
        """
        Set the row at the given position to the given note data.
        """
        return self.set_region(start=pos, end=pos, notes=notes, inclusive=True)

    def _measure_to_str(self, m, measure):
        rtn = []
        rows = _lcm(*[r[0].denominator for r in measure])
        for r in [(m * 4 + Fraction(n, rows)) for n in xrange(rows * 4)]:
            if measure and measure[0][0] == r:
                rtn.append(measure.pop(0)[1])
            else:
                rtn.append('0' * self.arrows)
        return rtn
    
    def __iter__(self):
        return iter(self.notes)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
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

    Exposes attributes `stepstype`, `description`, `difficulty`, and `radar`
    as strings, `meter` as an integer, and `notes` as a `Notes` object.
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
    
    def __repr__(self):
        rtn = '<Chart: {type} {difficulty} {meter}'.format(
            type=self.stepstype,
            difficulty=self.difficulty,
            meter=self.meter,
            description=self.description,
        )
        if self.description:
            rtn += ' (%s)' % self.description
        return rtn + '>'
    
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return ('#NOTES:\n'
                '     {stepstype}:\n'
                '     {description}:\n'
                '     {difficulty}:\n'
                '     {meter}:\n'
                '     {radar}:\n'
                '{notes}\n;').format(
                    stepstype=self.stepstype,
                    description=self.description,
                    difficulty=self.difficulty,
                    meter=self.meter,
                    radar=self.radar,
                    notes=self.notes)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Charts(SimfileList):
    """
    Encapsulates a list of charts and provides methods for retrieving them.
    """
    def filter(self, difficulty=None, stepstype=None, meter=None,
               description=None):
        """
        Filter charts and return matches in a new Charts object.
        
        If no charts match the given criteria, returns an empty Charts object.
        """
        result = Charts()
        for chart in self:
            if (difficulty and not chart.difficulty == difficulty or
                    stepstype and not chart.stepstype == stepstype or
                    meter and not chart.meter == meter or
                    description and not chart.description == description):
                continue
            result.append(chart)
        return result
    
    def get(self, **kwargs):
        """
        Get a chart that matches the given criteria.
        
        Arguments are identical to those of `filter`. Raises ``LookupError``
        if any number of charts other than one are matched.
        """
        result = self.filter(**kwargs)
        if len(result) != 1:
            raise LookupError('%s charts match the given parameters' %
                len(result))
        return result[0]
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return '\n\n'.join(unicode(chart) for chart in self)


class Timing(SimfileList):
    """
    Encapsulates timing data as a list of [beat, value] lists.

    The sole constructor argument should be a string of BPM or stop values.
    
    >>> t = Timing('0.000=170.000')
    >>> t
    Timing([[Fraction(0, 1), Decimal('170.000')]])
    >>> print t
    0.000=170.000
    """
    def __init__(self, tdata):
        tlist = []
        for tline in tdata.split(','):
            t = tline.strip().split('=')
            if ''.join(t):
                tlist.append([decimal_to_192nd(t[0]), Decimal(t[1])])
        self.extend(tlist)

    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return ',\n'.join(
            '='.join((unicode(decimal_from_192nd(t[0])), unicode(t[1])))
            for t in self)


class Simfile(OrderedDict):
    """
    Encapsulates simfile data.

    If the `filename` argument is given, reads a simfile from the given file.
    If the `string` argument is given, parses the string instead. Passing both
    arguments is disallowed.
    """
    DEFAULT_RADAR = '0,0,0,0,0'
    filename = dirname = None
    charts = None

    def __init__(self, filename=None, string=None):
        super(Simfile, self).__init__()
        self.charts = Charts()
        msddata = None
        try:
            if filename:
                if string:
                    raise TypeError('Simfile() takes either a filename '
                                    'or a string -- not both')
                self.filename = filename
                self.dirname = os.path.dirname(filename)
                msddata = codecs.open(filename, 'r', 'utf-8')
            elif string:
                msddata = string
            else:
                # Empty simfile
                return
            # Iterate over simfile's parameters
            for param in MSDParser(msddata):
                # StepMania treats the first identifier case-insensitively,
                # and leading identifiers are traditionally all-caps
                param[0] = param[0].upper()
                # Charts go into self.charts
                if param[0] == 'NOTES':
                    self.charts.append(Chart(param))
                # BPMS and STOPS go into self, but with extra methods
                elif param[0] in ('BPMS', 'STOPS'):
                    self[param[0]] = Timing(param[1])
                # Everything else goes into self
                else:
                    self[param[0]] = ':'.join(param[1:])
        finally:
            if msddata and hasattr(msddata, 'close'):
                msddata.close()

    def save(self, filename=None):
        """
        Write the simfile to the filesystem.

        If the `filename` argument is given, it is used. If omitted, the
        simfile will be written to the file from which it was originally read,
        or a ``ValueError`` will be raised if it was read from a string.
        """
        filename = filename or self.filename
        if not filename:
            raise ValueError('no filename provided')
        with codecs.open(filename, 'w', 'utf-8') as output:
            output.write(unicode(self))
    
    def __repr__(self):
        rtn = '<Simfile'
        if 'TITLE' in self and self['TITLE']:
            rtn += ': ' + self['TITLE']
            if 'SUBTITLE' in self and self['SUBTITLE']:
                subtitle = self['SUBTITLE']
                if subtitle[0] not in '[({' or subtitle[-1] not in '])}':
                    subtitle = '(%s)' % subtitle
                rtn += ' ' + subtitle
        return rtn + '>'
    
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '\n\n'.join((
            '\n'.join('#%s:%s;' % param for param in self.items()),
            unicode(self.charts)
        ))

    def __eq__(self, other):
        """
        Test for equality with another Simfile.

        This only compares the parameters and charts, not the filenames or any
        other Simfile object attributes.
        """
        return (type(self) is type(other) and
                super(Simfile, self).__eq__(other) and
                self.charts == other.charts)