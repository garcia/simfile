import unittest

from .helpers import *
from .. import *
from ..timed import timed_note_iterator
from ...timing import Beat, TimingData


class TestTimedNoteStream(unittest.TestCase):
    def test_from_chart(self):
        timed_notes = list(timed_note_iterator(
            note_source=testing_chart(),
            timing_data=TimingData.from_simfile(testing_simfile()),
        ))

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
