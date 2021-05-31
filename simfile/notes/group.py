from collections import deque
from enum import Enum
from heapq import heappush, heappop
from itertools import groupby
from typing import Deque, Dict, Iterator, List, NamedTuple, FrozenSet, \
    Optional, Sequence, Tuple, Union

from . import Note, NoteType
from ..timing import Beat


__all__ = [
    'NoteWithTail', 'GroupedNotes', 'SameBeatNotes', 'OrphanedNoteException',
    'OrphanedNotes', 'group_notes', 'ungroup_notes',
]


class NoteWithTail(NamedTuple):
    """
    A hold/roll head note with its corresponding tail note.
    """
    beat: Beat
    column: int
    note_type: NoteType
    tail_beat: Beat


_NoteMaybeWithTail = Union[Note, NoteWithTail]
GroupedNotes = Sequence[_NoteMaybeWithTail]


class SameBeatNotes(Enum):
    """
    Choices for :func:`group_notes`' `same_beat_notes` parameter.
    
    When multiple notes land on the same beat...

    * `KEEP_SEPARATE`: each note is emitted separately
    * `JOIN_BY_NOTE_TYPE`: notes of the same type are emitted together
    * `JOIN_ALL`: all notes are emitted together
    """
    KEEP_SEPARATE = 1
    JOIN_BY_NOTE_TYPE = 2
    JOIN_ALL = 3


class OrphanedNoteException(Exception):
    """
    Raised by :func:`group_notes` to flag an orphaned head or tail note.
    """


class OrphanedNotes(Enum):
    """
    Choices for :func:`group_notes`' `orphaned_head|tail` parameters.

    When `join_heads_to_tails` is True and a head or tail note is
    missing its counterpart...

    * `RAISE_EXCEPTION`: raise :class:`OrphanedNoteException`
    * `KEEP_ORPHAN`: emit the orphaned :class:`Note`
    * `DROP_ORPHAN`: do not emit the orphaned note
    """
    RAISE_EXCEPTION = 1
    KEEP_ORPHAN = 2
    DROP_ORPHAN = 3


def group_notes(
    notes: Iterator[Note],
    *,
    include_note_types: FrozenSet[NoteType] = frozenset(NoteType),
    same_beat_notes: SameBeatNotes = SameBeatNotes.KEEP_SEPARATE,
    join_heads_to_tails: bool = False,
    orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
    orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION
) -> Iterator[GroupedNotes]:
    """
    Group notes that are often considered linked to one another.

    There are two kinds of connected notes: notes that occur on the
    same beat ("jumps") and hold/roll notes with their corresponding
    tails. Either or both of these connection types can be opted into
    using the constructor parameters.

    Generators produced by this class yield :class:`GroupedNotes`
    objects, rather than :class:`Note` objects. These are sequences
    that generally contain :class:`Note` and :class:`NoteWithTail`
    objects, although the output may be more restrained depending on
    the configuration.

    When `join_heads_to_tails` is set to True, tail notes are attached
    to their corresponding hold/roll heads as :class:`NoteWithTail`
    objects. The tail itself will not be emitted as a separate note.
    If a head or tail note is missing its counterpart, `orphaned_head`
    and `orphaned_tail` determine the behavior. (These parameters are
    ignored if `join_heads_to_tails` is omitted.)

    Refer to each enum's documentation for the other configuration
    options.
    """
    held_columns: Dict[int, Note] = {}
    buffer: Deque[_NoteMaybeWithTail] = deque()
    
    def flush() -> Iterator[_NoteMaybeWithTail]:
        if buffer:
            yield from buffer
            buffer.clear()
    
    def maybe_buffer(note) -> Iterator[_NoteMaybeWithTail]:
        if held_columns:
            buffer.append(note)
        else:
            yield from flush()
            yield note
    
    def flush_until_held_note() -> Iterator[_NoteMaybeWithTail]:
        held_notes = held_columns.values()
        if held_notes:
            while buffer[0] not in held_notes:
                yield buffer.popleft()
        else:
            yield from flush()
    
    def attach_tail(head: Note, tail: Note) -> None:
        h = buffer.index(head)
        buffer[h] = NoteWithTail(
            beat=head.beat,
            column=head.column,
            note_type=head.note_type,
            tail_beat=tail.beat,
        )
    
    def join_head_to_tail(
        maybe_head: Optional[Note],
        maybe_tail: Optional[Note]
    ) -> None:
        if not maybe_head:
            if orphaned_tail == OrphanedNotes.RAISE_EXCEPTION:
                raise OrphanedNoteException(maybe_tail)
            elif orphaned_tail == OrphanedNotes.KEEP_ORPHAN:
                if maybe_tail: buffer.append(maybe_tail)
            elif orphaned_tail == OrphanedNotes.DROP_ORPHAN:
                pass # Do nothing and the tail won't be emitted
            return
        head: Note = maybe_head

        if not maybe_tail or maybe_tail.note_type != NoteType.TAIL:
            if orphaned_head == OrphanedNotes.RAISE_EXCEPTION:
                raise OrphanedNoteException(head)
            elif orphaned_head == OrphanedNotes.KEEP_ORPHAN:
                pass # Do nothing and the head will be emitted as-is
            elif orphaned_head == OrphanedNotes.DROP_ORPHAN:
                buffer.remove(head)
            else:
                raise ValueError(orphaned_head)
            return
        tail: Note = maybe_tail

        attach_tail(head, tail)
    
    def join_heads_to_tails_(note_stream: Iterator[Note]) \
        -> Iterator[_NoteMaybeWithTail]:
        for note in note_stream:
            # In a well-formed chart, these two conditions should always be
            # equal, but we'll let `join_head_to_tail` decide how to handle
            # edge cases with orphaned heads / tails.
            if note.column in held_columns or note.note_type == NoteType.TAIL:
                head = held_columns.pop(note.column, None)
                join_head_to_tail(head, note)
                yield from flush_until_held_note()
            
            if note.note_type in (NoteType.HOLD_HEAD, NoteType.ROLL_HEAD):
                held_columns[note.column] = note
            
            if note.note_type != NoteType.TAIL:
                yield from maybe_buffer(note)

        # Clean up orphaned heads
        for head in held_columns.values():
            join_head_to_tail(head, None)
        
        yield from flush()

    def add_row(row: List[_NoteMaybeWithTail]) -> Iterator[GroupedNotes]:
        if same_beat_notes == SameBeatNotes.KEEP_SEPARATE:
            yield from [[note] for note in row]
        elif same_beat_notes == SameBeatNotes.JOIN_ALL:
            yield row
        elif same_beat_notes == SameBeatNotes.JOIN_BY_NOTE_TYPE:
            joined_note_types = set()
            for note in row:
                nt = note.note_type
                if nt in joined_note_types:
                    continue
                joined_note_types.add(nt)
                yield list(filter(lambda n: n.note_type == nt, row))

    notes = filter(
        lambda note: note.note_type in include_note_types,
        notes,
    )

    notes_maybe_with_tails: Iterator[_NoteMaybeWithTail]
    if join_heads_to_tails:
        notes_maybe_with_tails = join_heads_to_tails_(notes)
    else:
        notes_maybe_with_tails = notes
    
    for _, row in groupby(notes_maybe_with_tails, lambda note: note.beat):
        yield from add_row(list(row))


def ungroup_notes(
    grouped_notes: Iterator[GroupedNotes],
    *,
    orphaned_notes: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION
) -> Iterator[Note]:
    """
    Convert grouped notes back into a plain note stream.

    If a note falls within a :class:`NoteWithTail`'s head and tail (on
    the same column), it would cause the head and tail to be orphaned.
    `orphaned_notes` determines how to handle the splitting note:
    `KEEP_ORPHAN` will yield the note (allowing the head and tail notes
    to become orphans) and `DROP_ORPHAN` will drop the note (preserving
    the link between the head and tail notes).
    
    Note that this check only applies to heads and tails joined as a
    :class:`NoteAndTail`. If :func:`group_notes` was called without
    specifying `join_heads_to_tails`, specifying `orphaned_notes` here
    will have no effect. This mirrors how :func:`group_notes`'
    `orphaned_head` and `orphaned_tail` parameters behave.
    """
    pending_tails: List[Note] = [] # heap

    def check_orphan(note: Note) -> Iterator[Note]:
        if note.column in (t.column for t in pending_tails):
            if orphaned_notes == OrphanedNotes.RAISE_EXCEPTION:
                raise OrphanedNoteException(note)
            elif orphaned_notes == OrphanedNotes.KEEP_ORPHAN:
                pass # Let the splitting note be yielded below
            elif orphaned_notes == OrphanedNotes.DROP_ORPHAN:
                return # Don't yield the splitting note
        yield note

    for row in grouped_notes:
        for note in row:
            # Yield any pending tails that we've reached
            while pending_tails and pending_tails[0] < note:
                yield heappop(pending_tails)
            
            # Yield plain notes directly
            if isinstance(note, Note):
                yield from check_orphan(note)
            
            # Yield notes with tails as a head (now) and a tail (later)
            elif isinstance(note, NoteWithTail):
                yield from check_orphan(Note(
                    beat=note.beat,
                    column=note.column,
                    note_type=note.note_type,
                ))
                heappush(pending_tails, Note(
                    beat=note.tail_beat,
                    column=note.column,
                    note_type=NoteType.TAIL,
                ))
    
    # Yield any remaining pending tails
    while pending_tails:
        yield heappop(pending_tails)