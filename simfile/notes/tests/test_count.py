import unittest

from .helpers import *
from .. import *
from ..transform import *
from ..count import *


class TestNoteCounter(unittest.TestCase):
    def test_count_chart(self):
        nc = NoteCounter()
        count = nc.count_chart(testing_chart())
        self.assertEqual(19, count)
    
    def test_count_chart_with_multiple_calls(self):
        nc = NoteCounter()
        count = nc.count_chart(testing_chart())
        self.assertEqual(19, count)
        count = nc.count_chart(testing_chart())
        self.assertEqual(19, count)
    
    def test_constructor_include_note_types(self):
        nc = NoteCounter(include_note_types=set((NoteType.TAP,)))
        count = nc.count_chart(testing_chart())
        self.assertEqual(15, count)

    def test_constructor_same_beat_notes_join_by_note_type(self):
        nc = NoteCounter(
            include_note_types=set((NoteType.MINE, NoteType.TAIL)),
            same_beat_notes=SameBeatNotes.JOIN_BY_NOTE_TYPE,
        )
        count = nc.count_chart(testing_chart())
        self.assertEqual(4, count)
    
    def test_constructor_same_beat_notes_keep_separate(self):
        nc = NoteCounter(
            include_note_types=set((NoteType.MINE, NoteType.TAIL)),
            same_beat_notes=SameBeatNotes.KEEP_SEPARATE,
        )
        count = nc.count_chart(testing_chart())
        self.assertEqual(7, count)
    
    def test_constructor_same_beat_minimum_2(self):
        nc = NoteCounter(same_beat_minimum=2)
        count = nc.count_chart(testing_chart())
        self.assertEqual(4, count)
    
    def test_constructor_same_beat_minimum_3(self):
        nc = NoteCounter(same_beat_minimum=3)
        count = nc.count_chart(testing_chart())
        self.assertEqual(0, count)
