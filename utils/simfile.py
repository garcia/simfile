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
        with open(simfile) as simfile_h:
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
        return {'stepstype': param[1],
                'description': param[2],
                'difficulty': param[3],
                'meter': param[4],
                'radar': param[5],
                'notes': self._notes(param[6])}
    
    def get_notes(self, difficulty, stepstype=None, meter=None, desc=None):
        """Retrieve the specified chart.
        
        The difficulty argument is required. stepstype, meter, and
        desc(ription) can additionally be specified if the search must be
        narrowed further. In absolutely ambiguous cases where two charts
        cannot be differentiated by any of the above parameters, use
        get_notes_positional instead.
        
        Raises MultiInstanceError in ambiguous cases and NoChartError if no
        chart matched the given parameters. Otherwise the chart's values
        are returned as a dictionary.
        
        """
        chart = None
        for param in self.params:
            # Not a chart
            if param[0].upper() != 'NOTES':
                continue
            # Matching difficulty
            if param[3] == difficulty:
                # Check optional parameters
                if (stepstype and not param[1] == stepstype or
                    meter and not int(param[4]) == meter or
                    desc and not param[2] == desc):
                    continue
                # Already found a chart that fits the parameters
                if chart:
                    hint = 'try using get_notes_positional'
                    if chart['stepstype'] != param[1]:
                        hint = 'which stepstype'
                    elif chart['meter'] != int(param[4]):
                        hint = 'which meter'
                    elif chart['desc'] != param[2]:
                        hint = 'which description'
                    raise MultiInstanceError('Ambiguous parameters (%s?)' %
                                             hint)
                # Give the enumerated values names
                chart = self._chart_to_dict(param)
        if not chart:
            raise NoChartError('No chart fits the given parameters')
        return chart
    
    def get_notes_positional(self, position):
        """Retrieve the <position>th chart in the simfile.
        
        position is 0-indexed. Raises IndexError if position exceeds the
        number of charts. Otherwise the chart's values are returned as a
        dictionary.
        
        """
        charts_seen = 0
        for param in self.params:
            if param[0].upper() == 'NOTES':
                if charts_seen == position:
                    return self._chart_to_dict(param)
                charts_seen += 1
        # If the chart hasn't been found yet, that can only mean one thing
        raise IndexError('Index out of range (only %s chart%s)' %
                           (charts_seen, '' if charts_seen == 1 else 's'))