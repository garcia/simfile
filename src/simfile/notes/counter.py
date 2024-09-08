from typing import Callable, Iterator, Sequence

from simfile.notes.timed import TimedNote, time_chart, time_notes
from simfile.timing import Beat
from . import Note, NoteData, NoteType
from .group import NoteWithTail, OrphanedNotes, SameBeatNotes, group_notes
from ..types import AttachedChart


__all__ = [
    "count_steps",
    "count_taps",
    "count_jumps",
    "count_hands",
    "count_holds",
    "count_rolls",
    "count_mines",
    "count_fakes",
]


_COUNT_HANDS_NOTE_TYPES = (
    NoteType.TAP,
    NoteType.HOLD_HEAD,
    NoteType.ROLL_HEAD,
    NoteType.TAIL,
)


_COUNT_STEPS_NOTE_TYPES = (
    NoteType.TAP,
    NoteType.HOLD_HEAD,
    NoteType.ROLL_HEAD,
    NoteType.LIFT,
)

_COUNT_TAPS_NOTE_TYPES = (
    NoteType.TAP,
    NoteType.HOLD_HEAD,
    NoteType.ROLL_HEAD,
    NoteType.LIFT,
)


def _filter_notes(
    chart: AttachedChart, note_types: Sequence[NoteType], drop_fake: bool
) -> Iterator[Note]:
    timed_notes = time_chart(chart)

    def predicate(note: TimedNote):
        if drop_fake and not note.hittable:
            return False
        return note.note.note_type in note_types

    return (note.note for note in filter(predicate, timed_notes))


def count_taps(chart: AttachedChart):
    filtered_notes = _filter_notes(chart, _COUNT_TAPS_NOTE_TYPES, drop_fake=True)
    return sum(1 for _ in filtered_notes)


def count_steps(chart: AttachedChart):
    filtered_notes = _filter_notes(chart, _COUNT_STEPS_NOTE_TYPES, drop_fake=True)
    grouped_notes = group_notes(filtered_notes, same_beat_notes=SameBeatNotes.JOIN_ALL)
    return sum(1 for _ in grouped_notes)


def count_jumps(chart: AttachedChart):
    filtered_notes = _filter_notes(chart, _COUNT_STEPS_NOTE_TYPES, drop_fake=True)
    grouped_notes = group_notes(filtered_notes, same_beat_notes=SameBeatNotes.JOIN_ALL)
    return sum(1 for gn in grouped_notes if len(gn) > 2)


def count_hands(chart: AttachedChart):
    active_tailed_notes: list[NoteWithTail] = []
    hands = 0

    # TODO(ash): figure out if we need to do something fancier
    # to account for a fake region partially intersecting a hold or roll
    for note_group in group_notes(
        _filter_notes(chart, _COUNT_HANDS_NOTE_TYPES, drop_fake=True),
        same_beat_notes=SameBeatNotes.JOIN_ALL,
        join_heads_to_tails=True,
        orphaned_head=OrphanedNotes.KEEP_ORPHAN,
        orphaned_tail=OrphanedNotes.DROP_ORPHAN,
    ):
        beat = note_group[0].beat

        # Remove holds / rolls whose tails have since passed
        active_tailed_notes = list(filter((lambda t: t[1] > beat), active_tailed_notes))

        # Are there 3 or more total active notes?
        if len(active_tailed_notes) + len(note_group) >= 3:
            hands += 1

        # Track any new holds / rolls
        for note in note_group:
            if isinstance(note, NoteWithTail):
                active_tailed_notes.append(note)

    return hands


def count_holds(chart: AttachedChart):
    filtered_notes = _filter_notes(chart, (NoteType.HOLD_HEAD,), drop_fake=True)
    return sum(1 for note in filtered_notes)


def count_rolls(chart: AttachedChart):
    filtered_notes = _filter_notes(chart, (NoteType.ROLL_HEAD,), drop_fake=True)
    return sum(1 for note in filtered_notes)


def count_mines(chart: AttachedChart):
    filtered_notes = _filter_notes(chart, (NoteType.MINE,), drop_fake=True)
    return sum(1 for note in filtered_notes)


def count_fakes(chart: AttachedChart):
    return sum(1 if not note.hittable else 0 for note in time_chart(chart))
