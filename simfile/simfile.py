from __future__ import with_statement, unicode_literals
import codecs
import collections
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


def _lcm(*numbers):
    def lcm(a, b):
        return (a * b) // reduce(gcd, (a, b))
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


class Notes(list):
    """
    The Notes class provides access to note data as a list of [beat, line]
    lists.

    Notes objects can be created from strings of .SM note data or from other
    Notes objects. For details on note data string formatting, see
    `the StepMania wiki <http://www.stepmania.com/wiki/The_.SM_file_format>`_.
    Creating a Notes object from an existing Notes object will clone it.
    """
    def _sort(self):
        self.sort(key=lambda x: x[0])

    def _clean_line(self, line):
        # Remove unnecessary whitespace
        line = line.strip()
        # The line may be empty; use filter(None, ...) to account for this
        return line

    def __init__(self, notedata=None):
        super(Notes, self).__init__()
        self.arrows = None

        if not notedata:
            return

        # Iterate over measures
        for m, measuredata in enumerate(notedata.split(',')):
            measure_lines = filter(None,
                (self._clean_line(line) for line in measuredata.splitlines()))
            measure_len = len(measure_lines)
            # Iterate over lines of measure
            for l, line in enumerate(measure_lines):
                line_pos = (m + Fraction(l, measure_len)) * 4
                # Set the number of arrows to the first line's length
                if self.arrows is None:
                    self.arrows = len(line)
                elif len(line) != self.arrows:
                    raise ValueError("Inconsistent row length at beat %s" %
                                     line_pos)
                # Ignore blank lines (e.g. "0000")
                if any(a != '0' for a in line):
                    super(Notes, self).append([line_pos, line])
    
    def _measure_to_str(self, m, measure):
        rtn = []
        rows = _lcm(*[r[0].denominator for r in measure])
        for r in [(m * 4 + Fraction(n, rows)) for n in xrange(rows * 4)]:
            if measure and measure[0][0] == r:
                rtn.append(measure.pop(0)[1])
            else:
                rtn.append('0' * self.arrows)
        return rtn
    
    def __repr__(self):
        # Don't try to output the entire list
        return object.__repr__(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        self._sort()
        rtn = []
        measure = []
        m = 0
        for row in self:
            # Usually this will only get executed once at a time, but if
            # there's an empty measure it'll execute twice or more.
            while row[0] / 4 >= m + 1:
                rtn.extend(self._measure_to_str(m, measure))
                rtn.append(',')
                measure = []
                m += 1
            measure.append(row)
        rtn.extend(self._measure_to_str(m, measure))
        return '\n'.join(rtn)

    def __eq__(self, other):
        return (type(self) is type(other) and
                super(Notes, self).__eq__(other) and
                self.arrows == other.arrows)


class Chart(object):
    """
    The Chart class represents chart metadata through its attributes.
    
    Chart objects can be created from lists, mappings (i.e. dicts), and other
    Chart objects. Lists should be of the form [stepstype, description,
    difficulty, meter, radar, notes]; mappings should have those items as keys.
    Creating a Chart from an existing Chart will clone it, including its
    `notes` attribute.

    `stepstype` is a string indicating the game mode of the chart.
    "dance-single" and "dance-double" are two common values. `description` can
    be set to any string. `difficulty` is a string indicating which difficulty
    slot the chart goes under -- traditionally one of "Beginner", "Easy",
    "Medium", "Hard", "Challenge", or "Edit", although this is not enforced.
    `meter` is an arbitrary positive integer that represents the chart's
    relative difficulty. `radar` is a string generated by StepMania that tries
    to break down difficulty into five components, although it can be safely
    set to an empty string. `notes` is a string of note data or a Notes object.
    """
    attrs = {
        'stepstype': unicode,
        'description': unicode,
        'difficulty': unicode,
        'meter': int,
        'radar': unicode,
        'notes': Notes,
    }
    
    def _from_list(self, chart):
        self.stepstype = chart[0]
        self.description = chart[1]
        self.difficulty = chart[2]
        self.meter = int(chart[3])
        self.radar = chart[4]
        self.notes = Notes(chart[5])
    
    def __init__(self, chart):
        if isinstance(chart, Chart):
            chart_get = chart.__getattribute__
        elif isinstance(chart, collections.Mapping):
            chart_get = chart.__getitem__
        elif isinstance(chart, collections.Sequence):
            return self._from_seq(chart)
        else:
            raise TypeError('Chart.__init__ takes a Chart, mapping, '
                            'or sequence')
        for attr, attr_type in Chart.attrs.items():
            getattr(self, attr) = chart_get(attr)
    
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
    The Charts class provides methods for retrieving Chart objects.
    
    In addition to the `filter` and `get` methods, Charts objects can be
    iterated over or indexed like lists.
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
    The Timing class provides sequential access to BPMS and STOPS parameters as
    a list of [beat, value] lists.

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
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return ',\n'.join(
            '='.join((unicode(decimal_from_192nd(t[0])), unicode(t[1])))
            for t in self)


class Simfile(OrderedDict):
    """
    The Simfile class encapsulates simfile parameters and charts.

    Simfile objects can be created from filenames or file-like objects. They
    can also be created from strings containing simfile data using the
    `from_string` class method.
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
                    self.charts.append(Chart(param[1:]))
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
    
    def __len__(self):
        """
        Get the combined length of the simfile's parameters and charts.
        
        A simfile containing neither parameters nor charts is considered empty.
        """
        return super(Simfile, self).__len__() + len(self.charts)
    
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