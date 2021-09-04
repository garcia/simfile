"""
Note data classes, plus submodules that operate on note data.
"""
from enum import Enum
from functools import reduce, total_ordering
from itertools import groupby
from io import StringIO
from math import gcd
from typing import Iterator, List, NamedTuple, Optional, Tuple, Type

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


class NoteData:
    """
    Wrapper for note data with iteration & serialization capabilities.
    """
    _notedata: str
    _columns: int

    @property
    def columns(self):
        """How many note columns this chart has."""
        return self._columns

    def __init__(self, notedata: str):
        self._notedata = notedata
        self._columns = NoteData._get_columns(notedata)
    
    @staticmethod
    def _get_columns(notes: str):
        first_comma = notes.find(',')
        first_measure = notes[:first_comma] if first_comma > 0 else notes
        first_line = first_measure.strip().splitlines()[0].strip()
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
            chars = ['0'] * columns
            for note in row:
                chars[note.column] = str(note.note_type)
            notedata.write(''.join(chars))
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
        """
        return cls(chart.notes)

    def update_chart(self, chart: Chart) -> None:
        chart.notes = str(self)
    
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
            # Check for keysound indexes (only relevant for keysounded charts)
            keysound_indexes: List[Optional[int]] = [None] * self._columns
            while '[' in line:
                opening_bracket = line.index('[')
                closing_bracket = line.index(']')
                keysound_index = int(line[opening_bracket+1:closing_bracket])
                # As long as there are no earlier brackets, the string index of
                # the opening bracket is always 1 greater than its note column
                keysound_indexes[opening_bracket-1] = keysound_index
                # To maintain the invariant described above (and to enable the
                # loop below), remove the bracket pair & number from the line
                line = line[:opening_bracket] + line[closing_bracket+1:]

            for c, column in enumerate(line):
                if column != '0':
                    yield Note(
                        beat=Beat(m*4*subdivision + l*4, subdivision),
                        column=c,
                        note_type=NoteType(column),
                        player=p,
                        keysound_index=keysound_indexes[c],
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
