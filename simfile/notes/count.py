from typing import FrozenSet, Iterator

from . import Note, NoteType
from .group import GroupedNotes, SameBeatNotes, OrphanedNotes, group_notes
from ..types import Chart


__all__ = [
    'count_grouped_notes', 'count_steps', 'count_jumps', 'count_mines',
    'count_hands', 'count_holds', 'count_rolls',
]


def count_grouped_notes(
    grouped_notes_iterator: Iterator[GroupedNotes],
    same_beat_minimum: int = 1,
) -> int:
    return sum(len(gn) >= same_beat_minimum for gn in grouped_notes_iterator)


DEFAULT_NOTE_TYPES: FrozenSet[NoteType] = frozenset((
    NoteType.TAP,
    NoteType.HOLD_HEAD,
    NoteType.ROLL_HEAD,
    NoteType.LIFT,
))


def count_steps(
    notes: Iterator[Note],
    *,
    include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
    same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
    same_beat_minimum: int = 1,
) -> int:
    """
    Count the number of notes in the supplied charts or note streams.

    The definition of "note count" varies by application; the default
    configuration tries to match StepMania's definition as closely as
    possible:
    
    * Taps, holds, rolls, and lifts are eligible for counting.
    * Multiple inputs on the same beat are only counted once.

    These defaults can be changed using the keyword parameters.
    """
    return count_grouped_notes(
        group_notes(
            notes,
            include_note_types=include_note_types,
            same_beat_notes=same_beat_notes,
        ),
        same_beat_minimum=same_beat_minimum,
    )


def count_jumps(
    notes: Iterator[Note],
    *,
    include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
    same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
) -> int:
    return count_steps(
        notes,
        include_note_types=include_note_types,
        same_beat_notes=same_beat_notes,
        same_beat_minimum=2,
    )


def count_mines(notes: Iterator[Note]) -> int:
    return sum(note.note_type == NoteType.MINE for note in notes)


def count_hands(
    notes: Iterator[Note],
    *,
    include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
    same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
    same_beat_minimum: int = 3
) -> int:
    return count_steps(
        notes,
        include_note_types=include_note_types,
        same_beat_notes=same_beat_notes,
        same_beat_minimum=same_beat_minimum,
    )


def _count_holds_or_rolls(
    notes: Iterator[Note],
    head: NoteType,
    *,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION
) -> int:
    return count_grouped_notes(
        group_notes(
            notes,
            include_note_types=frozenset((head, NoteType.TAIL)),
            join_heads_to_tails=True,
            orphaned_head=orphaned_head,
            orphaned_tail=orphaned_tail,
        ),
    )


def count_holds(
    notes: Iterator[Note],
    *,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION
) -> int:
    return _count_holds_or_rolls(
        notes,
        NoteType.HOLD_HEAD,
        orphaned_head=orphaned_head,
        orphaned_tail=orphaned_tail,
    )


def count_rolls(
    notes: Iterator[Note],
    *,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION
) -> int:
    return _count_holds_or_rolls(
        notes,
        NoteType.ROLL_HEAD,
        orphaned_head=orphaned_head,
        orphaned_tail=orphaned_tail,
    )