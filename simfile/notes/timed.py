from typing import Iterator, NamedTuple

from . import Note, NoteData
from ..timing import TimingData
from ..timing.engine import SongTime, TimingEngine
from ..types import Simfile, Chart


__all__ = ['TimedNote', 'timed_note_iterator']


class TimedNote(NamedTuple):
    """
    A note with its song time attached.
    """
    time: SongTime
    note: Note


def timed_note_iterator(
    note_data: NoteData,
    timing_data: TimingData
) -> Iterator[TimedNote]:
    """
    Generate a stream of timed notes from the supplied note & timing data.

    If a note is unhittable due to a warp segment, it won't be yielded.
    """
    engine = TimingEngine(timing_data)

    for note in note_data:
        if engine.hittable(note.beat):
            yield TimedNote(time=engine.time_at(note.beat), note=note)
