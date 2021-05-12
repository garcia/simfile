from typing import FrozenSet

from . import NoteType, NoteStream, NoteGenerator
from .transform import NoteGrouper, SameBeatNotes, OrphanedNotes
from ..types import Chart


__all__ = [
    'NoteCounter', 'StepCounter', 'JumpCounter', 'HoldCounter', 'MineCounter',
    'HandCounter', 'RollCounter',
]


class NoteCounter:
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

    same_beat_minimum: int
    _note_grouper: NoteGrouper

    def __init__(
        self,
        *,
        include_note_types: FrozenSet[NoteType] = DEFAULT_NOTE_TYPES,
        same_beat_notes: SameBeatNotes = SameBeatNotes.JOIN_ALL,
        join_heads_to_tails: bool = False,
        orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
        orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
        same_beat_minimum: int = 1,
    ):
        self.same_beat_minimum = same_beat_minimum
        self._note_grouper = NoteGrouper(
            include_note_types=include_note_types,
            same_beat_notes=same_beat_notes,
            join_heads_to_tails=join_heads_to_tails,
            orphaned_head=orphaned_head,
            orphaned_tail=orphaned_tail,
        )
    
    def count_notes(self, notes: NoteGenerator) -> int:
        """
        Tally all the notes in a note stream, adding to any note count
        already stored in the counter.
        """
        count = 0
        for grouped_notes in self._note_grouper.add_notes(notes):
            if len(grouped_notes) >= self.same_beat_minimum:
                count += 1
        return count

    def count_chart(self, chart: Chart) -> int:
        return self.count_notes(NoteStream.from_chart(chart))


class StepCounter(NoteCounter):
    def __init__(self):
        super().__init__()


class JumpCounter(NoteCounter):
    def __init__(self):
        super().__init__(same_beat_minimum=2)


class HoldCounter(NoteCounter):
    def __init__(self):
        super().__init__(
            note_types=frozenset((NoteType.HOLD_HEAD,)),
            same_beat_notes=SameBeatNotes.KEEP_SEPARATE,
        )


class MineCounter(NoteCounter):
    def __init__(self):
        super().__init__(
            note_types=frozenset((NoteType.MINE,)),
            same_beat_notes=SameBeatNotes.KEEP_SEPARATE,
        )


class HandCounter(NoteCounter):
    def __init__(self, same_beat_minimum=3):
        super().__init__(same_beat_minimum=same_beat_minimum)


class RollCounter(NoteCounter):
    def __init__(self):
        super().__init__(
            note_types=frozenset((NoteType.ROLL_HEAD,)),
            same_beat_notes=SameBeatNotes.KEEP_SEPARATE,
        )