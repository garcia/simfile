from enum import Enum
from typing import NamedTuple, Generator

from ..timing import Beat
from ..types import Chart


__all__ = ['NoteType', 'Note', 'NoteGenerator', 'NoteStream']


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


NoteGenerator = Generator[Note, None, None]


class NoteStream(object):
    """
    Methods for generating streams of notes from a chart or note data.
    """
    @classmethod
    def from_note_data(cls, note_data: str) -> NoteGenerator:
        for m, measure in enumerate(note_data.split(',')):
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

    @classmethod
    def from_chart(cls, chart: Chart) -> NoteGenerator:
        return cls.from_note_data(chart.notes)
