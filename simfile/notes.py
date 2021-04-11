from enum import Enum
from itertools import groupby
from typing import NamedTuple, Generator, FrozenSet, Optional, Sequence

from .timing import Beat, SongTime, SimfileTiming
from .types import Chart, Simfile


__all__ = [
    'NoteType', 'Note', 'NoteStream', 'TimedNote', 'TimedNoteStream',
    'SameBeatNotes', 'NoteCounter',
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


class TimedNote(NamedTuple):
    """
    A note with its song time attached.
    """
    time: SongTime
    note: Note


TimedNoteGenerator = Generator[TimedNote, None, None]


class TimedNoteStream(object):
    """
    Class for generating a time-synchronized stream of notes from a chart,
    given the timing data in its simfile.
    """
    def __init__(self, simfile: Simfile):
        self.simfile_timing = SimfileTiming(simfile)

    def from_chart(self, chart: Chart) -> TimedNoteGenerator:
        for note in NoteStream.from_chart(chart):
            time = self.simfile_timing.time_at(note.beat)
            yield TimedNote(time=time, note=note)


class SameBeatNotes(Enum):
    """
    Configuration options for :class:`NoteCounter`'s `same_beat_notes`
    constructor parameter.
    
    When multiple notes land on the same beat...

    * `COUNT_ONCE`: only 1 is added to the note count
    * `COUNT_NOTE_TYPES`: 1 is added per unique note type
    * `COUNT_ALL`: 1 is added per input
    """
    COUNT_ONCE = 1
    COUNT_NOTE_TYPES = 2
    COUNT_ALL = 3


class NoteCounter(object):
    """
    Counts the number of notes in the supplied charts or note streams.

    The definition of "note count" varies by application; the default
    configuration tries to match StepMania's definition as closely as
    possible:
    
    * Taps, holds, rolls, and lifts are eligible for counting.
    * Multiple inputs on the same beat are only counted once.

    These defaults can be changed using the constructor's keyword
    parameters. For more nuanced note predicates or row logic, subclass
    and override the private methods.
    """

    DEFAULT_NOTE_TYPES: FrozenSet[NoteType] = frozenset((
        NoteType.TAP,
        NoteType.HOLD_HEAD,
        NoteType.ROLL_HEAD,
        NoteType.LIFT,
    ))

    note_types: FrozenSet[NoteType]
    same_beat_notes: SameBeatNotes
    same_beat_minimum: int
    count: int

    def __init__(
        self,
        *,
        note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
        same_beat_notes: SameBeatNotes = SameBeatNotes.COUNT_ONCE,
        same_beat_minimum: int = 1,
    ):
        self.note_types = note_types
        self.same_beat_notes = same_beat_notes
        self.same_beat_minimum = same_beat_minimum
        self.count = 0
    
    def _add_row(self, row: Sequence[Note]):
        if len(row) < self.same_beat_minimum:
            return
        
        if self.same_beat_notes == SameBeatNotes.COUNT_ONCE:
            self.count += 1
        elif self.same_beat_notes == SameBeatNotes.COUNT_NOTE_TYPES:
            self.count += len(set(note.note_type for note in row))
        elif self.same_beat_notes == SameBeatNotes.COUNT_ALL:
            self.count += len(row)
    
    def _note_predicate(self, note: Note):
        return note.note_type in self.note_types
    
    def add_note_stream(self, note_stream: NoteGenerator):
        """
        Tally all the notes in a note stream, adding to any note count
        already stored in the counter.
        """
        filtered_note_stream = filter(self._note_predicate, note_stream)
        row_stream = groupby(filtered_note_stream, lambda note: note.beat)
        for beat, row in row_stream:
            self._add_row(list(row))

    
    def add_chart(self, chart: Chart):
        """
        Tally all the notes in a chart, adding to any note count already
        stored in the counter.
        """
        return self.add_note_stream(NoteStream.from_chart(chart))
