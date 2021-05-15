from enum import Enum
from typing import Iterator, NamedTuple, Union

from ..timing import Beat
from ..types import Chart


__all__ = ['NoteType', 'Note', 'NoteSource', 'note_iterator']


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


NoteSource = Union[Chart, str]


def note_iterator(note_source: NoteSource) -> Iterator[Note]:
    """
    Generate a stream of notes from a chart or string of note data.
    """
    if isinstance(note_source, str):
        note_data = note_source
    else:
        note_data = note_source.notes

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
