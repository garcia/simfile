from typing import FrozenSet, Iterable, Iterator

from . import Note, NoteType
from .group import GroupedNotes, SameBeatNotes, OrphanedNotes, group_notes


__all__ = [
    "count_grouped_notes",
    "count_steps",
    "count_jumps",
    "count_mines",
    "count_hands",
    "count_holds",
    "count_rolls",
]


def count_grouped_notes(
    grouped_notes_iterator: Iterable[GroupedNotes],
    same_beat_minimum: int = 1,
) -> int:
    """
    Count a stream of :class:`.GroupedNotes`.

    To count only groups of N or more notes, use `same_beat_minimum`.
    """
    return sum(len(gn) >= same_beat_minimum for gn in grouped_notes_iterator)


DEFAULT_NOTE_TYPES: FrozenSet[NoteType] = frozenset(
    (
        NoteType.TAP,
        NoteType.HOLD_HEAD,
        NoteType.ROLL_HEAD,
        NoteType.LIFT,
    )
)


def count_steps(
    notes: Iterable[Note],
    *,
    include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
    same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
    same_beat_minimum: int = 1,
) -> int:
    """
    Count the steps in a note stream.

    The definition of "step count" varies by application; the default
    configuration tries to match StepMania's definition as closely as
    possible:

    * Taps, holds, rolls, and lifts are eligible for counting.
    * Multiple inputs on the same beat are only counted once.

    These defaults can be changed using the keyword parameters. Refer
    to :class:`.SameBeatNotes` for alternative ways to count same-beat
    notes.
    """
    return count_grouped_notes(
        group_notes(
            filter(lambda note: note.note_type in include_note_types, notes),
            same_beat_notes=same_beat_notes,
        ),
        same_beat_minimum=same_beat_minimum,
    )


def count_jumps(
    notes: Iterable[Note],
    *,
    include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
    same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
) -> int:
    """
    Count the jumps (2+ simultaneous notes) in a note stream.

    This implementation defers to :func:`count_steps` with the same
    default parameters, except only groups of 2 or more notes are
    counted (i.e. `same_beat_minimum` is set to 2).
    """
    return count_steps(
        notes,
        include_note_types=include_note_types,
        same_beat_notes=same_beat_notes,
        same_beat_minimum=2,
    )


def count_mines(notes: Iterable[Note]) -> int:
    """
    Count the mines in a note stream.
    """
    return sum(note.note_type == NoteType.MINE for note in notes)


def count_hands(
    notes: Iterable[Note],
    *,
    include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
    same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
    same_beat_minimum: int = 3,
) -> int:
    """
    Count the hands (3+ simultaneous notes) in a note stream.

    This implementation defers to :func:`count_steps` with the same
    default parameters, except only groups of 3 or more notes are
    counted (i.e. `same_beat_minimum` is set to 3).
    """
    return count_steps(
        notes,
        include_note_types=include_note_types,
        same_beat_notes=same_beat_notes,
        same_beat_minimum=same_beat_minimum,
    )


def _count_holds_or_rolls(
    notes: Iterable[Note],
    head: NoteType,
    *,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
) -> int:
    return count_grouped_notes(
        filter(
            lambda singleton_group: singleton_group[0].note_type == head,
            group_notes(
                notes,
                join_heads_to_tails=True,
                orphaned_head=orphaned_head,
                orphaned_tail=orphaned_tail,
            ),
        ),
    )


def count_holds(
    notes: Iterable[Note],
    *,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.DROP_ORPHAN,
) -> int:
    """
    Count the hold notes in a note stream.

    By default, this method validates that hold heads connect to their
    corresponding tails. This validation can be turned off by setting
    the `orphaned_head` and `orphaned_tail` arguments; see
    :class:`.OrphanedNotes` for more details.
    """
    return _count_holds_or_rolls(
        notes,
        NoteType.HOLD_HEAD,
        orphaned_head=orphaned_head,
        orphaned_tail=orphaned_tail,
    )


def count_rolls(
    notes: Iterable[Note],
    *,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.DROP_ORPHAN,
) -> int:
    """
    Count the roll notes in a note stream.

    By default, this method validates that roll heads connect to their
    corresponding tails. This validation can be turned off by setting
    the `orphaned_head` and `orphaned_tail` arguments; see
    :class:`.OrphanedNotes` for more details.
    """
    return _count_holds_or_rolls(
        notes,
        NoteType.ROLL_HEAD,
        orphaned_head=orphaned_head,
        orphaned_tail=orphaned_tail,
    )
