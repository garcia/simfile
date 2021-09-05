"""
Note data classes, plus submodules that operate on note data.
"""
from enum import Enum
from functools import reduce, total_ordering
from itertools import groupby
from io import StringIO
from math import gcd
from simfile.base import BaseChart
from typing import Iterator, List, NamedTuple, Optional, Tuple, Type, Union

from ..timing import Beat
from ..types import Chart


__all__ = ['NoteType', 'Note', 'NoteData']


class NoteType(Enum):
    """
    Known note types supported by StepMania.
    """
    TAP = '1'
    HOLD_HEAD = '2'
    TAIL = '3'
    ROLL_HEAD = '4'
    ATTACK = 'A'
    FAKE = 'F'
    KEYSOUND = 'K'
    LIFT = 'L'
    MINE = 'M'

    def __str__(self):
        """Returns the character value of the note type."""
        return self.value
    
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'
    

@total_ordering
class Note(NamedTuple):
    """
    A note, corresponding to a nonzero character in a chart's note data.

    Note objects are intrinsically ordered according to their position in
    the underlying note data: that is, if `note1` would appear earlier in
    the note data string than `note2`, then `note1 < note2` is true.
    """
    beat: Beat
    column: int
    note_type: NoteType
    
    player: int = 0
    """
    Only used in routine charts. The second player's note data will have
    this value set to 1.
    """

    keysound_index: Optional[int] = None
    """
    Only used in keysounded SSC charts. Notes followed by a number in square
    brackets will have this value set to the bracketed number.
    """

    def _comparable(self) -> Tuple[int, Beat, int]:
        return (self.player, self.beat, self.column)

    def __lt__(self, other) -> bool:
        # bool(...) wrapper to satisfy mypy
        return bool(self._comparable() < other._comparable())
    
    def __str__(self):
        '''
        Returns the note string as it would appear in note data.

        Includes the note type's character, followed by a bracketed keysound
        index if present.
        '''
        note_string = str(self.note_type)
        if self.keysound_index is not None:
            note_string += f'[{self.keysound_index}]'
        return note_string
    
    def __repr__(self):
        return f'{self.__class__.__name__}(' + ', '.join(filter(None, (
            f'beat={repr(self.beat)}',
            f'column={self.column}',
            f'note_type={repr(self.note_type)}',
            f'player={self.player}' if self.player != 0 else None,
            f'keysound_index={self.keysound_index}' if self.keysound_index is not None else None,
        ))) + ')'
            


class NoteData:
    """
    Wrapper for note data with iteration & serialization capabilities.

    The constructor accepts a string of note data, any :data:`.Chart`, or
    another :class:`NoteData` instance.
    """
    _notedata: str
    _columns: int

    @property
    def columns(self):
        """How many note columns this chart has."""
        return self._columns

    def __init__(self, source: Union[str, Chart, 'NoteData']):
        if isinstance(source, str):
            self._notedata = source
        elif isinstance(source, BaseChart):
            if source.notes is None:
                raise ValueError('chart has no notes')
            self._notedata = source.notes
        elif isinstance(source, NoteData):
            self._notedata = source._notedata
        else:
            raise TypeError('expected str, Chart, or NoteData')

        self._columns = NoteData._get_columns(self._notedata)
    
    @staticmethod
    def _get_columns(notes: str):
        first_comma = notes.find(',')
        first_measure = notes[:first_comma] if first_comma > 0 else notes
        first_line = first_measure.strip().splitlines()[0].strip()
        first_line = NoteData._extract_keysound_indices(first_line)
        return len(first_line)
    
    @classmethod
    def from_notes(
        cls: Type['NoteData'],
        notes: Iterator[Note],
        columns: int
    ) -> 'NoteData':
        """
        Convert a stream of notes into note data.

        This method assumes the following preconditions:

        * The input notes are naturally sorted.
        * Every note's beat is nonnegative.
        * Every note's column is nonnegative and less than `columns`.

        Note that this method doesn't quantize beats to 192nd ticks,
        and off-grid notes may result in measures with more rows than
        the StepMania editor would produce. StepMania will quantize
        these notes gracefully during gameplay, but you can apply
        :meth:`.Beat.round_to_tick` to each note's beat
        if you'd prefer to keep the note data tidy.
        """
        notedata = StringIO()

        # write a row and trailing newline to the notedata
        def push_row(row: List[Note] = []):
            note_strings = ['0'] * columns
            for note in row:
                note_strings[note.column] = str(note)
            notedata.write(''.join(note_strings))
            notedata.write('\n')

        # write a measure to the notedata (no commas or newlines of its own)
        def push_measure(measure: List[Note] = []):
            # get all beat quantizations from this measure
            quantizations = map(lambda note: note.beat.denominator, measure)
            # find the least common multiple of these quantizations
            q = reduce(lambda a, b: a * b // gcd(a, b), quantizations, 1)
            
            # group notes by row
            # the expression `note.beat % 4 * q` should always resolve to an
            # integer because `q` is a multiple of every beat's denominator
            last_row = -1
            for r, row in groupby(measure, lambda note: int(note.beat % 4 * q)):
                # account for any skipped beats
                for _ in range(last_row+1, r):
                    push_row()
                push_row(list(row))
                last_row = r
            # account for any trailing empty rows
            for _ in range(last_row+1, q*4):
                push_row()
        
        # group notes by player (for routine charts)
        last_player = -1
        for p, player_notes in groupby(notes, lambda n: n.player):
            if p > last_player:
                if last_player > -1:
                    notedata.write('&\n')
                # account for any skipped players
                for _ in range(last_player+1, p):
                    push_measure()
                    notedata.write('&\n')
                last_player = p
            
            # group notes by measure
            last_measure = -1
            for m, measure in groupby(player_notes, lambda n: n.beat // 4):
                # handling the comma at the start of the loop instead of the end
                # avoids needing to know when we've reached the last measure
                if last_measure > -1:
                    notedata.write(',\n')
                # account for any skipped measures
                for _ in range(last_measure+1, m):
                    push_measure()
                    notedata.write(',\n')
                push_measure(list(measure))
                last_measure = m
            
            # if there were no notes at all, write a blank measure
            if last_measure == -1:
                push_measure()
        
        return cls(notedata.getvalue())

    @classmethod
    def from_chart(cls: Type['NoteData'], chart: Chart) -> 'NoteData':
        """
        Get note data from a chart.

        .. deprecated:: 2.0.0-beta.7
           Use :code:`NoteData(chart)` instead.
        """
        return cls(chart.notes)

    def update_chart(self, chart: Chart) -> None:
        """
        Replace the note data in the chart with this object's note data.

        .. deprecated:: 2.0.0-beta.7
           Use :code:`chart.notes = str(notedata)` instead.
        """
        chart.notes = str(self)
    
    # Returns the line without keysound indices and optionally populates the
    # provided list with the indices
    @staticmethod
    def _extract_keysound_indices(
        line: str,
        keysound_indices: Optional[List[Optional[int]]] = None,
    ) -> str:
        while '[' in line:
            opening_bracket = line.index('[')
            closing_bracket = line.index(']')
            keysound_index = int(line[opening_bracket+1:closing_bracket])
            # As long as there are no earlier brackets, the string index of
            # the opening bracket is always 1 greater than its note column
            if keysound_indices is not None:
                keysound_indices[opening_bracket-1] = keysound_index
            # To maintain the invariant described above (and to construct
            # the un-keysounded line), remove the bracket pair & number
            line = line[:opening_bracket] + line[closing_bracket+1:]
        return line
    
    def _iter_measure(
        self,
        p: int,         # player index
        m: int,         # measure index
        measure: str,   # the measure, stripped of whitespace
    ) -> Iterator[Note]:
        lines = measure.splitlines()
        subdivision = len(lines)
        
        for l, line in enumerate(lines):
            line = line.strip()
            keysound_indices: List[Optional[int]] = [None] * self._columns
            line = NoteData._extract_keysound_indices(line, keysound_indices)

            for c, column in enumerate(line):
                if column != '0':
                    yield Note(
                        beat=Beat(m*4*subdivision + l*4, subdivision),
                        column=c,
                        note_type=NoteType(column),
                        player=p,
                        keysound_index=keysound_indices[c],
                    )

    def __iter__(self) -> Iterator[Note]:
        """
        Iterate over the notes in the note data.

        Notes are yielded chronologically (ascending beats) first, then
        in ascending column order (same as the serialized order).
        """
        # "Routine" steps types (currently dance-routine and pump-routine) use
        # an & marker to separate the two players' steps. All other steps types
        # do not use an &, so `p` will only be 0 the vast majority of the time
        # TODO: str.split is space-inefficient - consider alternatives
        for p, notedata in enumerate(self._notedata.split('&')):
            for m, measure in enumerate(notedata.split(',')):
                yield from self._iter_measure(p, m, measure.strip())
    
    def __str__(self) -> str:
        """Returns the note data string."""
        return self._notedata
