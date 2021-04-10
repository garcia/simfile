from enum import Enum
from typing import NamedTuple, Generator

from .timing import Beat, SongTime, SimfileTiming
from .types import Chart, Simfile


__all__ = ['NoteType', 'Note', 'NoteStream', 'TimedNote', 'TimedNoteStream']


class NoteType(Enum):
    TAP = '1'
    HOLD_HEAD = '2'
    TAIL = '3'
    ROLL_HEAD = '4'
    FAKE = 'F'
    KEYSOUND = 'K'
    LIFT = 'L'
    MINE = 'M'
    

class Note(NamedTuple):
    beat: Beat
    column: int
    note_type: NoteType


class NoteStream(object):
    @classmethod
    def from_str(cls, notes_str: str) -> Generator[Note, None, None]:
        for m, measure in enumerate(notes_str.split(',')):
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
    def from_chart(cls, chart: Chart) -> Generator[Note, None, None]:
        return cls.from_str(chart.notes)


class TimedNote(NamedTuple):
    time: SongTime
    note: Note


class TimedNoteStream(object):
    def __init__(self, simfile: Simfile):
        self.simfile_timing = SimfileTiming(simfile)

    def from_chart(self, chart: Chart) -> Generator[TimedNote, None, None]:
        for note in NoteStream.from_chart(chart):
            time = self.simfile_timing.time_at(note.beat)
            yield TimedNote(time=time, note=note)