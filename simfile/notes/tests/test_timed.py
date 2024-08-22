from decimal import Decimal
import unittest

from .helpers import *
from .. import *
from ..timed import time_notes, TimedNote
from ...timing import Beat, BeatValue, TimingData


class TestTimeNotes(unittest.TestCase):
    def test_time_notes(self):
        timed_notes = list(
            time_notes(
                note_data=NoteData(testing_chart()),
                timing_data=TimingData(testing_simfile()),
            )
        )

        self.assertAlmostEqual(4.000, timed_notes[0].time)
        self.assertEqual(
            Note(beat=Beat(16, 4), column=0, note_type=NoteType.TAP),
            timed_notes[0].note,
        )
        self.assertAlmostEqual(4.250, timed_notes[1].time)
        self.assertEqual(
            Note(beat=Beat(18, 4), column=2, note_type=NoteType.TAP),
            timed_notes[1].note,
        )
        self.assertAlmostEqual(9.000, timed_notes[-1].time)
        self.assertEqual(
            Note(beat=Beat(48, 4), column=3, note_type=NoteType.TAIL),
            timed_notes[-1].note,
        )

    def test_time_notes_with_notes_inside_warp(self):
        timing_data = TimingData(testing_simfile())
        timing_data.warps.append(BeatValue(Beat(4), Decimal(2.5)))
        timed_notes = list(
            time_notes(
                note_data=NoteData(testing_chart()),
                timing_data=timing_data,
            )
        )

        self.assertAlmostEqual(4.000, timed_notes[0].time)
        self.assertEqual(
            Note(beat=Beat(16, 4), column=0, note_type=NoteType.TAP),
            timed_notes[0].note,
        )
        self.assertFalse(timed_notes[0].hittable)

        self.assertAlmostEqual(4.000, timed_notes[1].time)
        self.assertEqual(
            Note(beat=Beat(18, 4), column=2, note_type=NoteType.TAP),
            timed_notes[1].note,
        )
        self.assertFalse(timed_notes[1].hittable)

        self.assertAlmostEqual(4.000, timed_notes[2].time)
        self.assertEqual(
            Note(beat=Beat(20, 4), column=1, note_type=NoteType.HOLD_HEAD),
            timed_notes[2].note,
        )
        self.assertFalse(timed_notes[2].hittable)

        self.assertAlmostEqual(7.750, timed_notes[-1].time)
        self.assertEqual(
            Note(beat=Beat(48, 4), column=3, note_type=NoteType.TAIL),
            timed_notes[-1].note,
        )
        self.assertTrue(timed_notes[-1].hittable)

    def test_time_notes_with_notes_inside_fake_region(self):
        timing_data = TimingData(testing_simfile())
        timing_data.fakes.append(BeatValue(Beat(4), Decimal(2.5)))
        timed_notes = list(
            time_notes(
                note_data=NoteData(testing_chart()),
                timing_data=timing_data,
            )
        )

        self.assertAlmostEqual(4.000, timed_notes[0].time)
        self.assertEqual(
            Note(beat=Beat(16, 4), column=0, note_type=NoteType.TAP),
            timed_notes[0].note,
        )
        self.assertFalse(timed_notes[0].hittable)

        self.assertAlmostEqual(4.000, timed_notes[1].time)
        self.assertEqual(
            Note(beat=Beat(18, 4), column=2, note_type=NoteType.TAP),
            timed_notes[1].note,
        )
        self.assertFalse(timed_notes[1].hittable)

        self.assertAlmostEqual(4.000, timed_notes[2].time)
        self.assertEqual(
            Note(beat=Beat(20, 4), column=1, note_type=NoteType.HOLD_HEAD),
            timed_notes[2].note,
        )
        self.assertFalse(timed_notes[2].hittable)

        self.assertAlmostEqual(7.750, timed_notes[-1].time)
        self.assertEqual(
            Note(beat=Beat(48, 4), column=3, note_type=NoteType.TAIL),
            timed_notes[-1].note,
        )
        self.assertTrue(timed_notes[-1].hittable)
