from enum import Enum
from typing import Iterator, NamedTuple

from . import Note, NoteData, NoteType
from ..timing import TimingData
from ..timing.engine import SongTime, TimingEngine


__all__ = ["TimedNote", "time_notes"]


class TimedNote(NamedTuple):
    """
    A note with its song time attached.
    """

    time: SongTime
    note: Note
    hittable: bool


def time_notes(
    note_data: NoteData,
    timing_data: TimingData,
) -> Iterator[TimedNote]:
    """
    Generate a stream of timed notes from the supplied note & timing data.
    """
    engine = TimingEngine(timing_data)

    for note in note_data:
        hittable = engine.hittable(note.beat)
        yield TimedNote(
            time=engine.time_at(note.beat),
            note=note,
            hittable=hittable,
        )
