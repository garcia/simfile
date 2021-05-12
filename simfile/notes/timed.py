from typing import Generator, NamedTuple

from . import Note, NoteStream
from ..timing import SongTime, SimfileTiming
from ..types import Simfile, Chart


__all__ = ['TimedNote', 'TimedNoteGenerator', 'TimedNoteStream']


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
