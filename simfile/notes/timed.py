from simfile.ssc import SSCChart
from typing import Generator, Iterator, NamedTuple

from . import Note, NoteSource, note_iterator
from ..timing import SongTime, SimfileTiming
from ..types import Simfile, Chart


__all__ = ['TimedNote', 'TimedNoteStream']


class TimedNote(NamedTuple):
    """
    A note with its song time attached.
    """
    time: SongTime
    note: Note


def timed_note_iterator(
    note_source: NoteSource,
    timing_source: Simfile
) -> Iterator[TimedNote]:
    """
    Generate a time-synchronized stream of notes from the timing data
    in its simfile.
    """
    timing = SimfileTiming(timing_source)

    for note in note_iterator(note_source):
        time = timing.time_at(note.beat)
        yield TimedNote(time=time, note=note)
