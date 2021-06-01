from enum import Enum
from functools import reduce, total_ordering
from itertools import groupby
from io import StringIO
from math import gcd
from typing import Iterator, List, NamedTuple, Type

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
    
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'
    

@total_ordering
class Note(NamedTuple):
    """
    A note, corresponding to a nonzero character in a chart's note data.
    """
    beat: Beat
    column: int
    note_type: NoteType

    def __lt__(self, other) -> bool:
        """
        Compare to another note first by beat, then by column.
        """
        if self.beat < other.beat:
            return True
        if self.beat == other.beat:
            if self.column < other.column:
                return True
        return False


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

        * The input notes are sorted chronologically (ascending beats).
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
                chars[note.column] = note.note_type.value
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
        
        # group notes by measure
        last_measure = -1
        for m, measure in groupby(notes, lambda n: n.beat // 4):
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
        if 'NOTES2' in chart:
            return cls(chart['NOTES2'])
        else:
            return cls(chart.notes)

    def update_chart(self, chart: Chart) -> None:
        # SSC charts with keysounds use a separate "NOTES2" property
        # which should be mutually exclusive with "NOTES"
        if 'NOTES2' in chart:
            chart['NOTES2'] = str(self)
        else:
            chart.notes = str(self)

    def __iter__(self) -> Iterator[Note]:
        """
        Iterate over the notes in the note data.

        Notes are yielded chronologically (ascending beats) first, then
        in ascending column order (same as the serialized order).
        """
        for m, measure in enumerate(self._notedata.split(',')):
            lines = measure.strip().splitlines()
            subdivision = len(lines)
            for l, line in enumerate(lines):
                for c, column in enumerate(line.strip()):
                    if column != '0':
                        yield Note(
                            beat=Beat(m*4*subdivision + l*4, subdivision),
                            column=c,
                            note_type=NoteType(column),
                        )
    
    def __str__(self) -> str:
        """Returns the note data string."""
        return self._notedata
