from enum import Enum
from typing import NamedTuple, Generator, FrozenSet, Optional

from .timing import Beat, SongTime, SimfileTiming
from .types import Chart, Simfile


__all__ = [
    'NoteType', 'Note', 'NoteStream', 'TimedNote', 'TimedNoteStream',
    'NoteCounter',
]


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


class NoteCounter(object):
    DEFAULT_NOTE_TYPES: FrozenSet[NoteType] = frozenset((
        NoteType.TAP,
        NoteType.HOLD_HEAD,
        NoteType.ROLL_HEAD,
        NoteType.LIFT,
    ))

    note_types: FrozenSet[NoteType]
    count_jumps_once: bool
    count: int
    _previous_beat: Optional[Beat]

    def __init__(
        self,
        *,
        note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
        count_jumps_once: bool = True,
    ):
        self.note_types = note_types
        self.count_jumps_once = count_jumps_once
        self.count = 0
        self._previous_beat = None
    
    def add_note(self, note: Note):
        """
        Tally a note, if it matches the note counter's constraints.

        Notes are expected to be added sequentially; non-sequential notes
        will likely break counting jumps once.
        """
        if note.note_type not in self.note_types:
            return
        if note.beat == self._previous_beat and self.count_jumps_once:
            return
        self.count += 1
        self._previous_beat = note.beat
    
    def add_chart(self, chart: Chart):
        """
        Tally all the notes in a chart, adding to any note count already
        stored in the counter.
        """
        # Reset previous beat in case we're tallying multiple charts
        self._previous_beat = None
        for note in NoteStream.from_chart(chart):
            self.add_note(note)
