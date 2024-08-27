import unittest

from .helpers import *
from simfile.notes import *
from simfile.notes.group import SameBeatNotes
from simfile.notes.count import *


class TestNoteCounter(unittest.TestCase):
    def test_count_steps(self):
        count = count_steps(testing_notes())
        self.assertEqual(19, count)

    def test_count_steps_include_note_types(self):
        count = count_steps(
            testing_notes(), include_note_types=frozenset((NoteType.TAP,))
        )
        self.assertEqual(15, count)

    def test_count_steps_same_beat_notes_join_by_note_type(self):
        count = count_steps(
            testing_notes(),
            include_note_types=frozenset((NoteType.MINE, NoteType.TAIL)),
            same_beat_notes=SameBeatNotes.JOIN_BY_NOTE_TYPE,
        )
        self.assertEqual(4, count)

    def test_count_steps_same_beat_notes_keep_separate(self):
        count = count_steps(
            testing_notes(),
            include_note_types=frozenset((NoteType.MINE, NoteType.TAIL)),
            same_beat_notes=SameBeatNotes.KEEP_SEPARATE,
        )
        self.assertEqual(7, count)

    def test_count_steps_same_beat_minimum_2(self):
        count = count_steps(testing_notes(), same_beat_minimum=2)
        self.assertEqual(4, count)

    def test_count_steps_same_beat_minimum_3(self):
        count = count_steps(testing_notes(), same_beat_minimum=3)
        self.assertEqual(0, count)

    def test_count_holds_and_rolls(self):
        hold_count = count_holds(testing_notes())
        roll_count = count_rolls(testing_notes())
        self.assertEqual(1, hold_count)
        self.assertEqual(2, roll_count)
