from typing import Iterator, NamedTuple

from . import Note, NoteSource, note_iterator
from ..timing import SongTime, TimingConverter, TimingData
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
    timing_data: TimingData
) -> Iterator[TimedNote]:
    """
    Generate a time-synchronized stream of notes from the timing data
    in its simfile.
    """
    timing = TimingConverter(timing_data)

    for note in note_iterator(note_source):
        time = timing.time_at(note.beat)
        yield TimedNote(time=time, note=note)
