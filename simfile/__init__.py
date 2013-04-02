import codecs
import os

__all__ = ['MultiInstanceError', 'NoChartError', 'Param', 'Notes', 'Simfile']

# Used internally
def enum(*sequential, **named):
    """Creates an enum out of both sequential and named elements."""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# Special exceptions
class MultiInstanceError(Exception): pass
class NoChartError(Exception): pass


class Param(list):
    """Represents a parameter as a list of values.
    
    This class is identical to `list` but includes a special __str__ method.
    """
    def __str__(self):
        if self[0].upper() == 'NOTES':
            return ('\n#' + ':\n     '.join(self[:-1]) + ':\n' + self[-1] + ';')
        else:
            return ('#' + ':'.join(self) + ';')


class Notes(list):
    """Represents note data as a list of measures, which are lists of rows.
    
    This class is identical to `list` but includes a special __str__ method.
    """
    def __str__(self):
        return '\n,\n'.join(['\n'.join(m) for m in self]) + '\n'


class Simfile(object):
    
    DEFAULT_RADAR = u'0,0,0,0,0'
    states = enum('NEXT_PARAM', 'READ_VALUE', 'COMMENT')
    
    def __init__(self, simfile):
        """Read and parse the given simfile.
        
        The functionality of this code should mirror StepMania's
        MsdFile.cpp fairly closely.
        
        """
        # TODO: support for .SSC, .DWI, etc.
        # This will probably involve separating the MSD parser from this code
        self.filename = simfile
        self.dirname = os.path.dirname(simfile)
		
        with codecs.open(simfile, encoding='utf-8') as simfile_h:
            sf = simfile_h.read()
        state = self.states.NEXT_PARAM
        params = []
        i = 0
        for i, c in enumerate(sf):
            # Start of comment
            if i + 1 < len(sf) and c == '/' and sf[i + 1] == '/':
                old_state = state
                state = self.states.COMMENT
            # Comment
            elif state == self.states.COMMENT:
                if c in '\r\n':
                    state = old_state
            # Start of parameter
            if state == self.states.NEXT_PARAM:
                if c == '#':
                    state = self.states.READ_VALUE
                    param = ['']
            # Read value
            elif state == self.states.READ_VALUE:
                # Fix missing semicolon
                if c == '#' and sf[i - 1] in '\r\n':
                    param[-1] = param[-1].strip()
                    params.append(Param(param))
                    param = ['']
                # Next value
                elif c == ':':
                    param[-1] = param[-1].strip()
                    param.append('')
                # Next parameter
                elif c == ';':
                    param[-1] = param[-1].strip()
                    params.append(Param(param))
                    state = self.states.NEXT_PARAM
                # Add character to param
                else:
                    param[-1] += c
        self.params = params
    
    def get(self, identifier):
        """Retrieve the value(s) denoted by (and including) the identifier.
        
        Raises KeyError if there is no such identifier and
        MultiInstanceError if multiple parameters begin with the identifier
        or if it is known to be a multi-instance identifier (i.e. NOTES).
        
        Identifiers are case-insensitive.
        
        """
        identifier = identifier.upper()
        if identifier == 'NOTES':
            raise MultiInstanceError('Use get_chart for notedata')
        found_param = None
        for param in self.params:
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
    
    def _notes(self, notedata):
        """Converts a string of note data into a nested list."""
        notes = []
        for measure in notedata.split(','):
            notes.append([])
            for line in measure.splitlines():
                line = line.strip()
                if line.find('//') >= 0:
                    line = line.split('//', '1')[0]
                if line:
                    notes[-1].append(line)
        return Notes(notes)
    
    def get_raw_chart(self, difficulty=None, stepstype=None, meter=None,
                  description=None, index=None):
        """Retrieve the specified chart as an ordinary parameter.
        
        Raises MultiInstanceError in ambiguous cases, NoChartError if no
        chart matched the given parameters, and IndexError if an invalid
        index was given. Otherwise the chart's values are returned as a
        dictionary.
        
        """
        chart = None
        if index != None:
            i = 0
        for param in self.params:
            # Not a chart
            if param[0].upper() != 'NOTES':
                continue
            # Check parameters
            if ((difficulty and not param[3] == difficulty or
                 stepstype and not param[1] == stepstype or
                 meter and not int(param[4]) == meter or
                 description and not param[2] == description) and
                 any((difficulty, stepstype, meter, description))):
                continue
            # Already found a chart that fits the parameters
            if chart and index == None:
                hint = 'which index'
                if chart[1] != param[1]:
                    hint = 'which stepstype'
                elif chart[4] != int(param[4]):
                    hint = 'which meter'
                elif chart[2] != param[2]:
                    hint = 'which description'
                raise MultiInstanceError('Ambiguous parameters (%s?)' % hint)
            chart = param
            if index != None:
                if i == index:
                    return chart
                i += 1
        if not chart or index != None and i == 0:
            raise NoChartError('No charts fit the given parameters')
        if index != None:
            raise IndexError('Only %s charts fit the given parameters' % i)
        return chart
    
    def get_chart(self, difficulty=None, stepstype=None, meter=None,
                  description=None, index=None):
        """Retrieve the specified chart.
        
        difficulty, stepstype, meter, and/or description can all be
        specified to narrow a search for a specific chart. If the 'index'
        parameter is omitted, there must be exactly one chart that fits the
        given parameters. Otherwise, the <index>th matching chart is
        returned.
        
        Raises any error that get_raw_chart might raise.
        
        """
        chart = self.get_raw_chart(difficulty, stepstype, meter, description,
            index)
        # Give the enumerated values names
        return {'stepstype': chart[1],
                'description': chart[2],
                'difficulty': chart[3],
                'meter': int(chart[4]),
                'radar': chart[5],
                'notes': self._notes(chart[6])}
        
    def set_chart(self, notes, difficulty=None, stepstype=None, meter=None,
                  description=None, index=None, radar=None):
        """Change a chart from or add a chart to the simfile.
        
        The arguments are identical to those of get_chart, with the exception
        of the required 'notes' argument at the beginning and the optional
        'radar' argument at the end. The 'stepstype' argument is required when
        adding a new chart, but not when editing an existing chart (assuming
        the other given parameters are sufficiently unambiguous). The 'radar'
        argument is only used when adding a chart.
        
        Raises any error that get_raw_chart might raise, except for
        NoChartError.
        
        """
        found_chart = False
        try:
            chart = self.get_raw_chart(difficulty, stepstype, meter,
                                       description, index)
        except NoChartError:
            if not stepstype:
                raise ValueError("Must specify stepstype when adding a chart")
            chart = Param([
                'NOTES',
                stepstype,
                unicode(description) if description else u'synctools',
                unicode(difficulty) if difficulty else u'Edit',
                unicode(meter) if meter else u'1',
                unicode(radar) if radar else self.DEFAULT_RADAR,
                u''
            ])
        chart[6] = unicode(Notes(notes))
        if chart not in self.params:
            self.params.append(chart)
    
    def save(self):
        with codecs.open(self.filename, 'w', 'utf-8') as output:
            output.write(unicode(self))
    
    def __str__(self):
        return '\n'.join(unicode(param) for param in self.params)