import codecs

from synctools import enum

# Special exceptions
class MultiInstanceError(Exception): pass
class NoChartError(Exception): pass


class Param(list):
    def __str__(self):
        if self[0].upper() == 'NOTES':
            return ('\n#' + ':\n     '.join(self[:-1]) + ':\n' + self[-1] + ';')
        else:
            return ('#' + ':'.join(self) + ';')


class Notes(list):
    def __str__(self):
        return '\n,\n'.join(['\n'.join(m) for m in self])


class Simfile:
    # TODO: support for .SSC, .DWI, etc.
    # This will probably involve separating the MSD parser from this code
    states = enum('NEXT_PARAM', 'READ_VALUE', 'COMMENT')
    def __init__(self, simfile):
        """Read and parse the given simfile.
        
        The functionality of this code should mirror StepMania's
        MsdFile.cpp fairly closely.
        
        """
        self.simfile = simfile
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
        """Retrieve the value(s) following the identifier.
        
        Raises KeyError if there is no such identifier and
        MultiInstanceError if multiple parameters begin with the identifier
        or if it is known to be a multi-instance identifier (i.e. NOTES).
        
        Identifiers are case-insensitive.
        
        """
        identifier = identifier.upper()
        if identifier == 'NOTES':
            raise MultiInstanceError('Cannot get a multi-instance identifier')
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
        return notes
 
    def _chart_to_dict(self, param):
        """Converts a NOTES parameter to a dictionary."""
        return {'stepstype': param[1],
                'description': param[2],
                'difficulty': param[3],
                'meter': int(param[4]),
                'radar': param[5],
                'notes': self._notes(param[6])}
    
    def get_chart(self, difficulty=None, stepstype=None, meter=None,
                  description=None, index=None):
        """Retrieve the specified chart.
        
        difficulty, stepstype, meter, and/or description can all be
        specified to narrow a search for a specific chart. If the 'index'
        parameter is omitted, there must be exactly one chart that fits the
        given parameters. Otherwise, the <index>th matching chart is
        returned.
        
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
                if chart['stepstype'] != param[1]:
                    hint = 'which stepstype'
                elif chart['meter'] != int(param[4]):
                    hint = 'which meter'
                elif chart['description'] != param[2]:
                    hint = 'which description'
                raise MultiInstanceError('Ambiguous parameters (%s?)' % hint)
            # Give the enumerated values names
            chart = self._chart_to_dict(param)
            if index != None:
                if i == index:
                    return chart
                i += 1
        if not chart or index != None and i == 0:
            raise NoChartError('No charts fit the given parameters')
        if index != None:
            raise IndexError('Only %s charts fit the given parameters' % i)
        return chart