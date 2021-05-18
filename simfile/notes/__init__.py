from enum import Enum
from simfile._private.serializable import Serializable
from typing import Iterator, NamedTuple, Type, Union

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
    

class Note(NamedTuple):
    """
    A note, corresponding to a nonzero character in a chart's note data.
    """
    beat: Beat
    column: int
    note_type: NoteType


class NoteData:
    """
    Wrapper for note data with iteration & serialization capabilities.
    """
    _notes: str

    def __init__(self, notes: str):
        self._notes = notes
    
    @classmethod
    def from_chart(cls: Type['NoteData'], chart: Chart) -> 'NoteData':
        """
        Get note data from a chart.
        """
        return cls(chart.notes)

    def __iter__(self) -> Iterator[Note]:
        """
        Iterate over the notes in the note data.

        Notes are yielded chronologically first, then in ascending
        column order (same as the serialized order).
        """
        for m, measure in enumerate(self._notes.split(',')):
            lines = measure.strip().splitlines()
            subdivision = len(lines)
            for l, line in enumerate(lines):
                for c, column in enumerate(line.rstrip()):
                    if column != '0':
                        yield Note(
                            beat=Beat(m*4 + l*4/subdivision),
                            column=c,
                            note_type=NoteType(column),
                        )
    
    def __str__(self) -> str:
        return self._notes
