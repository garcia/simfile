import unittest

from .. import Note, NoteType, NoteData
from ..group import *
from ...timing import Beat


def testing_valid_notes():
    return NoteData(
        '1200\n'
        '0010\n'
        '0001\n'
        '0010\n'
        ',\n'
        '1300\n'
        '0001\n'
        '4004\n'
        '0010\n'
        ',\n'
        '3000\n'
        '1000\n'
        '0003\n'
        '0001\n'
        ',\n'
        '2000\n'
        '0200\n'
        '0010\n'
        '0001\n'
        ',\n'
        '0310\n'
        '0001\n'
        '3010\n'
        '1001\n'
    )


def testing_invalid_notes():
    return NoteData(
        '3000\n'
        '0200\n'
        '0200\n'
        '0304\n'
        ',\n'
        '2000\n'
        '1000\n'
        '3000\n'
        '0020\n'
    )

class TestGroupNotes(unittest.TestCase):
    def test_default_configuration(self):
        grouped_notes = list(group_notes(testing_valid_notes()))
        self.assertListEqual([
            [Note(beat=Beat(0), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(0), column=1, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(1), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(2), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(3), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(4), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(4), column=1, note_type=NoteType.TAIL)],
            [Note(beat=Beat(5), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(6), column=0, note_type=NoteType.ROLL_HEAD)],
            [Note(beat=Beat(6), column=3, note_type=NoteType.ROLL_HEAD)],
            [Note(beat=Beat(7), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(8), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(9), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(10), column=3, note_type=NoteType.TAIL)],
            [Note(beat=Beat(11), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(12), column=0, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(13), column=1, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(14), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(15), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(16), column=1, note_type=NoteType.TAIL)],
            [Note(beat=Beat(16), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(17), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(18), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(18), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(19), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(19), column=3, note_type=NoteType.TAP)],
        ], grouped_notes)
    
    def test_join_heads_to_tails(self):
        grouped_notes = list(group_notes(
            testing_valid_notes(),
            join_heads_to_tails=True,
        ))
        self.assertListEqual([
            [Note(beat=Beat(0), column=0, note_type=NoteType.TAP)],
            [NoteWithTail(beat=Beat(0), column=1, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(4))],
            [Note(beat=Beat(1), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(2), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(3), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(4), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(5), column=3, note_type=NoteType.TAP)],
            [NoteWithTail(beat=Beat(6), column=0, note_type=NoteType.ROLL_HEAD, tail_beat=Beat(8))],
            [NoteWithTail(beat=Beat(6), column=3, note_type=NoteType.ROLL_HEAD, tail_beat=Beat(10))],
            [Note(beat=Beat(7), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(9), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(11), column=3, note_type=NoteType.TAP)],
            [NoteWithTail(beat=Beat(12), column=0, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(18))],
            [NoteWithTail(beat=Beat(13), column=1, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(16))],
            [Note(beat=Beat(14), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(15), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(16), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(17), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(18), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(19), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(19), column=3, note_type=NoteType.TAP)],
        ], grouped_notes)
    
    def test_same_beat_notes_join_all(self):
        grouped_notes = list(group_notes(
            testing_valid_notes(),
            same_beat_notes=SameBeatNotes.JOIN_ALL,
        ))
        self.assertListEqual([
            [
                Note(beat=Beat(0), column=0, note_type=NoteType.TAP),
                Note(beat=Beat(0), column=1, note_type=NoteType.HOLD_HEAD),
            ],
            [Note(beat=Beat(1), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(2), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(3), column=2, note_type=NoteType.TAP)],
            [
                Note(beat=Beat(4), column=0, note_type=NoteType.TAP),
                Note(beat=Beat(4), column=1, note_type=NoteType.TAIL),
            ],
            [Note(beat=Beat(5), column=3, note_type=NoteType.TAP)],
            [
                Note(beat=Beat(6), column=0, note_type=NoteType.ROLL_HEAD),
                Note(beat=Beat(6), column=3, note_type=NoteType.ROLL_HEAD),
            ],
            [Note(beat=Beat(7), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(8), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(9), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(10), column=3, note_type=NoteType.TAIL)],
            [Note(beat=Beat(11), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(12), column=0, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(13), column=1, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(14), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(15), column=3, note_type=NoteType.TAP)],
            [
                Note(beat=Beat(16), column=1, note_type=NoteType.TAIL),
                Note(beat=Beat(16), column=2, note_type=NoteType.TAP),
            ],
            [Note(beat=Beat(17), column=3, note_type=NoteType.TAP)],
            [
                Note(beat=Beat(18), column=0, note_type=NoteType.TAIL),
                Note(beat=Beat(18), column=2, note_type=NoteType.TAP),
            ],
            [
                Note(beat=Beat(19), column=0, note_type=NoteType.TAP),
                Note(beat=Beat(19), column=3, note_type=NoteType.TAP),
            ],
        ], grouped_notes)
    
    def test_same_beat_notes_join_by_note_type(self):
        grouped_notes = list(group_notes(
            testing_valid_notes(),
            same_beat_notes=SameBeatNotes.JOIN_BY_NOTE_TYPE,
        ))
        self.assertListEqual([
            [Note(beat=Beat(0), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(0), column=1, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(1), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(2), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(3), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(4), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(4), column=1, note_type=NoteType.TAIL)],
            [Note(beat=Beat(5), column=3, note_type=NoteType.TAP)],
            [
                Note(beat=Beat(6), column=0, note_type=NoteType.ROLL_HEAD),
                Note(beat=Beat(6), column=3, note_type=NoteType.ROLL_HEAD),
            ],
            [Note(beat=Beat(7), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(8), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(9), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(10), column=3, note_type=NoteType.TAIL)],
            [Note(beat=Beat(11), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(12), column=0, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(13), column=1, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(14), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(15), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(16), column=1, note_type=NoteType.TAIL)],
            [Note(beat=Beat(16), column=2, note_type=NoteType.TAP)],
            [Note(beat=Beat(17), column=3, note_type=NoteType.TAP)],
            [Note(beat=Beat(18), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(18), column=2, note_type=NoteType.TAP)],
            [
                Note(beat=Beat(19), column=0, note_type=NoteType.TAP),
                Note(beat=Beat(19), column=3, note_type=NoteType.TAP),
            ],
        ], grouped_notes)
    
    def test_invalid_chart_join_heads_to_tails_raises(self):
        self.assertRaises(
            OrphanedNoteException,
            list,
            group_notes(testing_invalid_notes(), join_heads_to_tails=True),
        )
    
    def test_invalid_chart_keep_orphaned_heads_and_tails(self):
        grouped_notes = list(group_notes(
            testing_invalid_notes(),
            join_heads_to_tails=True,
            orphaned_head=OrphanedNotes.KEEP_ORPHAN,
            orphaned_tail=OrphanedNotes.KEEP_ORPHAN,
        ))
        self.assertListEqual([
            [Note(beat=Beat(0), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(1), column=1, note_type=NoteType.HOLD_HEAD)],
            [NoteWithTail(beat=Beat(2), column=1, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(3))],
            [Note(beat=Beat(3), column=3, note_type=NoteType.ROLL_HEAD)],
            [Note(beat=Beat(4), column=0, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(5), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(6), column=0, note_type=NoteType.TAIL)],
            [Note(beat=Beat(7), column=2, note_type=NoteType.HOLD_HEAD)],
        ], grouped_notes)
    
    def test_invalid_chart_drop_orphaned_heads_and_tails(self):
        grouped_notes = list(group_notes(
            testing_invalid_notes(),
            join_heads_to_tails=True,
            orphaned_head=OrphanedNotes.DROP_ORPHAN,
            orphaned_tail=OrphanedNotes.DROP_ORPHAN,
        ))
        self.assertListEqual([
            [NoteWithTail(beat=Beat(2), column=1, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(3))],
            [Note(beat=Beat(5), column=0, note_type=NoteType.TAP)],
        ], grouped_notes)
    
    def test_invalid_chart_drop_orphaned_heads_keep_orphaned_tails(self):
        grouped_notes = list(group_notes(
            testing_invalid_notes(),
            join_heads_to_tails=True,
            orphaned_head=OrphanedNotes.DROP_ORPHAN,
            orphaned_tail=OrphanedNotes.KEEP_ORPHAN,
        ))
        self.assertListEqual([
            [Note(beat=Beat(0), column=0, note_type=NoteType.TAIL)],
            [NoteWithTail(beat=Beat(2), column=1, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(3))],
            [Note(beat=Beat(5), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(6), column=0, note_type=NoteType.TAIL)],
        ], grouped_notes)
    
    def test_invalid_chart_keep_orphaned_heads_drop_orphaned_tails(self):
        grouped_notes = list(group_notes(
            testing_invalid_notes(),
            join_heads_to_tails=True,
            orphaned_head=OrphanedNotes.KEEP_ORPHAN,
            orphaned_tail=OrphanedNotes.DROP_ORPHAN,
        ))
        self.assertListEqual([
            [Note(beat=Beat(1), column=1, note_type=NoteType.HOLD_HEAD)],
            [NoteWithTail(beat=Beat(2), column=1, note_type=NoteType.HOLD_HEAD, tail_beat=Beat(3))],
            [Note(beat=Beat(3), column=3, note_type=NoteType.ROLL_HEAD)],
            [Note(beat=Beat(4), column=0, note_type=NoteType.HOLD_HEAD)],
            [Note(beat=Beat(5), column=0, note_type=NoteType.TAP)],
            [Note(beat=Beat(7), column=2, note_type=NoteType.HOLD_HEAD)],
        ], grouped_notes)


class TestUngroupNotes(unittest.TestCase):
    def test_with_valid_grouped_notes(self):
        notes = list(testing_valid_notes())
        grouped_notes = group_notes(
            notes,
            same_beat_notes=SameBeatNotes.JOIN_ALL,
            join_heads_to_tails=True,
        )
        ungrouped_notes = list(ungroup_notes(grouped_notes))

        self.assertListEqual(notes, ungrouped_notes)
    
    def test_with_invalid_grouped_notes(self):
        grouped_notes = [
            [NoteWithTail(
                beat=Beat(0),
                column=0,
                note_type=NoteType.TAP,
                tail_beat=Beat(2),
            )],
            [Note(beat=Beat(1), column=0, note_type=NoteType.TAP)],
        ]
        note_ungrouper = ungroup_notes(grouped_notes)

        self.assertRaises(OrphanedNoteException, list, note_ungrouper)
    
    def test_keep_orphaned_notes(self):
        grouped_notes = [
            [NoteWithTail(
                beat=Beat(0),
                column=0,
                note_type=NoteType.HOLD_HEAD,
                tail_beat=Beat(2),
            )],
            [Note(beat=Beat(1), column=0, note_type=NoteType.TAP)],
        ]
        ungrouped_notes = list(ungroup_notes(
            grouped_notes,
            orphaned_notes=OrphanedNotes.KEEP_ORPHAN,
        ))

        self.assertListEqual([
            Note(beat=Beat(0), column=0, note_type=NoteType.HOLD_HEAD),
            Note(beat=Beat(1), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(2), column=0, note_type=NoteType.TAIL),
        ], ungrouped_notes)
    
    def test_drop_orphaned_notes(self):
        grouped_notes = [
            [NoteWithTail(
                beat=Beat(0),
                column=0,
                note_type=NoteType.HOLD_HEAD,
                tail_beat=Beat(2),
            )],
            [Note(beat=Beat(1), column=0, note_type=NoteType.TAP)],
        ]
        ungrouped_notes = list(ungroup_notes(
            grouped_notes,
            orphaned_notes=OrphanedNotes.DROP_ORPHAN,
        ))

        self.assertListEqual([
            Note(beat=Beat(0), column=0, note_type=NoteType.HOLD_HEAD),
            Note(beat=Beat(2), column=0, note_type=NoteType.TAIL),
        ], ungrouped_notes)