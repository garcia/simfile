from enum import Enum
from typing import Iterator, NamedTuple

from . import Note, NoteData, NoteType
from ..timing import TimingData
from ..timing.engine import SongTime, TimingEngine


__all__ = ["TimedNote", "UnhittableNotes", "time_notes"]


class TimedNote(NamedTuple):
    """
    A note with its song time attached.
    """

    time: SongTime
    note: Note


class UnhittableNotes(Enum):
    """
    How to handle timed notes that are unhittable due to warp segments.

    When a note is unhittable...

    * `TAP_TO_FAKE`: convert tap notes to fakes, drop other note types
    * `DROP_NOTE`: drop the unhittable note regardless of type
    * `KEEP_NOTE`: keep the unhittable note
    """

    TAP_TO_FAKE = 1
    DROP_NOTE = 2
    KEEP_NOTE = 3


def time_notes(
    note_data: NoteData,
    timing_data: TimingData,
    unhittable_notes: UnhittableNotes = UnhittableNotes.TAP_TO_FAKE,
) -> Iterator[TimedNote]:
    """
    Generate a stream of timed notes from the supplied note & timing data.

    For notes that are unhittable due to warps, the `unhittable_notes`
    parameter determines the behavior. See :class:`UnhittableNotes` for
    more details.
    """
    engine = TimingEngine(timing_data)

    for note in note_data:
        if engine.hittable(note.beat) or unhittable_notes == UnhittableNotes.KEEP_NOTE:
            yield TimedNote(time=engine.time_at(note.beat), note=note)
        elif unhittable_notes == UnhittableNotes.TAP_TO_FAKE:
            if note.note_type == NoteType.TAP:
                yield TimedNote(
                    time=engine.time_at(note.beat),
                    note=Note(
                        beat=note.beat,
                        column=note.column,
                        note_type=NoteType.FAKE,
                    ),
                )
