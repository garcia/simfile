import unittest

from .helpers import *
from .. import *
from ..timed import *
from ...timing import Beat


class TestTimedNoteStream(unittest.TestCase):
    def test_from_chart(self):
        timed_note_stream = TimedNoteStream(testing_simfile())
        timed_notes = list(timed_note_stream.from_chart(testing_chart()))

        self.assertAlmostEqual(4.000, timed_notes[0].time)
        self.assertEqual(
            Note(beat=Beat(16,4), column=0, note_type=NoteType.TAP),
            timed_notes[0].note
        )
        self.assertAlmostEqual(4.250, timed_notes[1].time)
        self.assertEqual(
            Note(beat=Beat(18,4), column=2, note_type=NoteType.TAP),
            timed_notes[1].note
        )
        self.assertAlmostEqual(9.000, timed_notes[-1].time)
        self.assertEqual(
            Note(beat=Beat(48,4), column=3, note_type=NoteType.TAIL),
            timed_notes[-1].note
        )
