import abc
from collections import deque
from enum import Enum
from itertools import groupby
from typing import Deque, Dict, List, NamedTuple, Generator, FrozenSet, \
    Optional, Sequence, Union

from . import Note, NoteType, NoteStream, NoteGenerator
from ..timing import Beat
from ..types import Chart


__all__ = [
    'NoteTransformer', 'NoteFilterer', 'NoteTypeFilterer', 'NoteWithTail',
    'GroupedNotes', 'GroupedNotesGenerator', 'SameBeatNotes',
    'OrphanedNoteException', 'OrphanedNotes', 'NoteGrouper',
]


class NoteTransformer:
    def add_notes(self, note_stream: NoteGenerator) -> NoteGenerator:
        """
        Consume notes from a note generator, such as those returned by
        :class:`NoteStream`'s class methods.

        This base implementation simply yields the note stream untouched.
        """
        yield from note_stream
    
    def add_chart(self, chart: Chart) -> NoteGenerator:
        """
        Consume notes from a chart's note data.
        """
        yield from self.add_notes(NoteStream.from_chart(chart))


class NoteFilterer(NoteTransformer):
    @abc.abstractmethod
    def predicate(self, note: Note) -> bool:
        """
        Decide whether to keep or drop each note in the stream.
        """
    
    def add_notes(self, note_stream: NoteGenerator):
        yield from filter(self.predicate, note_stream)


class NoteTypeFilterer(NoteFilterer):
    include_note_types: FrozenSet[NoteType]

    def __init__(
        self,
        *,
        include_note_types: FrozenSet[NoteType] = frozenset(NoteType),
    ):
        self.include_note_types = include_note_types
    
    def predicate(self, note: Note) -> bool:
        return note.note_type in self.include_note_types


class NoteWithTail(NamedTuple):
    """
    A hold/roll head note with its corresponding tail note, if present.
    """
    beat: Beat
    column: int
    note_type: NoteType
    tail_beat: Beat


_NoteMaybeWithTail = Union[Note, NoteWithTail]
_NoteMaybeWithTailGenerator = Generator[_NoteMaybeWithTail, None, None]


GroupedNotes = Sequence[_NoteMaybeWithTail]
GroupedNotesGenerator = Generator[GroupedNotes, None, None]


class SameBeatNotes(Enum):
    """
    Configuration options for :class:`NoteGrouper`'s `same_beat_notes`
    constructor parameter.
    
    When multiple notes land on the same beat...

    * `KEEP_SEPARATE`: each note is emitted separately
    * `JOIN_BY_NOTE_TYPE`: notes of the same type are emitted together
    * `JOIN_ALL`: all notes are emitted together
    """
    KEEP_SEPARATE = 1
    JOIN_BY_NOTE_TYPE = 2
    JOIN_ALL = 3


class OrphanedNoteException(Exception):
    pass


class OrphanedNotes(Enum):
    """
    Configuration options for :class:`NoteGrouper`'s `orphaned_head`
    and `orphaned_tail` constructor parameters.

    When a head or tail note is missing its counterpart...

    * `RAISE_EXCEPTION`: raise :class:`OrphanedNoteException`
    * `KEEP_ORPHAN`: emit the orphaned :class:`Note`
    * `DROP_ORPHAN`: do not emit the orphaned note
    """
    RAISE_EXCEPTION = 1
    KEEP_ORPHAN = 2
    DROP_ORPHAN = 3


class NoteGrouper(NoteTypeFilterer):
    """
    Groups notes that are often considered linked to one another.

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

    Refer to each enum's documentation for the other configuration
    options.
    """
    same_beat_notes: SameBeatNotes
    join_heads_to_tails: bool
    orphaned_head: OrphanedNotes
    orphaned_tail: OrphanedNotes

    _held_columns: Dict[int, Note]
    _buffer: Deque[_NoteMaybeWithTail]

    def __init__(
        self,
        *,
        include_note_types: FrozenSet[NoteType] = frozenset(NoteType),
        same_beat_notes: SameBeatNotes = SameBeatNotes.KEEP_SEPARATE,
        join_heads_to_tails: bool = False,
        orphaned_head: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION,
        orphaned_tail: OrphanedNotes = OrphanedNotes.RAISE_EXCEPTION
    ):
        super().__init__(include_note_types=include_note_types)
        self.same_beat_notes = same_beat_notes
        self.join_heads_to_tails = join_heads_to_tails
        self.orphaned_head = orphaned_head
        self.orphaned_tail = orphaned_tail
        self._held_columns = {}
        self._buffer = deque()
    
    def _flush(self) -> _NoteMaybeWithTailGenerator:
        if self._buffer:
            yield from self._buffer
            self._buffer.clear()
    
    def _maybe_buffer(self, note) -> _NoteMaybeWithTailGenerator:
        if self._held_columns:
            self._buffer.append(note)
        else:
            yield from self._flush()
            yield note
    
    def _flush_until_held_note(self) -> _NoteMaybeWithTailGenerator:
        held_notes = self._held_columns.values()
        if held_notes:
            while self._buffer[0] not in held_notes:
                yield self._buffer.popleft()
        else:
            yield from self._flush()
    
    def _attach_tail(self, head: Note, tail: Note) -> None:
        h = self._buffer.index(head)
        self._buffer[h] = NoteWithTail(
            beat=head.beat,
            column=head.column,
            note_type=head.note_type,
            tail_beat=tail.beat,
        )
    
    def _join_head_to_tail(
        self,
        maybe_head: Optional[Note],
        maybe_tail: Optional[Note]
    ) -> None:
        if not maybe_head:
            if self.orphaned_tail == OrphanedNotes.RAISE_EXCEPTION:
                raise OrphanedNoteException(maybe_tail)
            elif self.orphaned_tail == OrphanedNotes.KEEP_ORPHAN:
                if maybe_tail: self._buffer.append(maybe_tail)
            elif self.orphaned_tail == OrphanedNotes.DROP_ORPHAN:
                pass # Do nothing and the tail won't be emitted
            return
        head: Note = maybe_head

        if not maybe_tail or maybe_tail.note_type != NoteType.TAIL:
            if self.orphaned_head == OrphanedNotes.RAISE_EXCEPTION:
                raise OrphanedNoteException(head)
            elif self.orphaned_head == OrphanedNotes.KEEP_ORPHAN:
                pass # Do nothing and the head will be emitted as-is
            elif self.orphaned_head == OrphanedNotes.DROP_ORPHAN:
                self._buffer.remove(head)
            else:
                raise ValueError(self.orphaned_head)
            return
        tail: Note = maybe_tail

        self._attach_tail(head, tail)
    
    def _join_heads_to_tails(
        self,
        note_stream: NoteGenerator,
    ) -> _NoteMaybeWithTailGenerator:
        for note in note_stream:
            # In a well-formed chart, these two conditions should always be
            # equal, but we'll let `_join_head_to_tail` decide how to handle
            # edge cases with orphaned heads / tails.
            if note.column in self._held_columns or note.note_type == NoteType.TAIL:
                head = self._held_columns.pop(note.column, None)
                self._join_head_to_tail(head, note)
                yield from self._flush_until_held_note()
            
            if note.note_type in (NoteType.HOLD_HEAD, NoteType.ROLL_HEAD):
                self._held_columns[note.column] = note
            
            if note.note_type != NoteType.TAIL:
                yield from self._maybe_buffer(note)

        # Clean up orphaned heads
        for head in self._held_columns.values():
            self._join_head_to_tail(head, None)
        
        yield from self._flush()

    def _add_row(self, row: List[_NoteMaybeWithTail]) -> GroupedNotesGenerator:
        if self.same_beat_notes == SameBeatNotes.KEEP_SEPARATE:
            yield from [[note] for note in row]
        elif self.same_beat_notes == SameBeatNotes.JOIN_ALL:
            yield row
        elif self.same_beat_notes == SameBeatNotes.JOIN_BY_NOTE_TYPE:
            joined_note_types = set()
            for note in row:
                nt = note.note_type
                if nt in joined_note_types:
                    continue
                joined_note_types.add(nt)
                yield list(filter(lambda n: n.note_type == nt, row))

    def add_notes(self, notes: NoteGenerator) -> GroupedNotesGenerator: # type: ignore
        """
        Tally all the notes in a note stream, adding to any note count
        already stored in the counter.
        """
        notes = super().add_notes(notes)
        
        notes_maybe_with_tails: _NoteMaybeWithTailGenerator
        if self.join_heads_to_tails:
            notes_maybe_with_tails = self._join_heads_to_tails(notes)
        else:
            notes_maybe_with_tails = notes
        
        for _, row in groupby(notes_maybe_with_tails, lambda note: note.beat):
            yield from self._add_row(list(row))
