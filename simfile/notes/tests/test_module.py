from simfile.ssc import SSCChart
from textwrap import indent
import unittest

from .helpers import *
from .. import *
from ...timing import Beat


class TestNoteStream(unittest.TestCase):
    def test_from_chart(self):
        notes = list(NoteData.from_chart(testing_chart()))
        self.assertListEqual([
            Note(beat=Beat(16,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(18,4), column=2, note_type=NoteType.TAP),
            Note(beat=Beat(20,4), column=1, note_type=NoteType.HOLD_HEAD),
            Note(beat=Beat(22,4), column=3, note_type=NoteType.TAP),
            Note(beat=Beat(24,4), column=1, note_type=NoteType.TAIL),
            Note(beat=Beat(24,4), column=2, note_type=NoteType.TAP),
            Note(beat=Beat(28,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(28,4), column=3, note_type=NoteType.TAP),
            Note(beat=Beat(30,4), column=1, note_type=NoteType.MINE),
            Note(beat=Beat(30,4), column=2, note_type=NoteType.MINE),
            Note(beat=Beat(32,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(33,4), column=1, note_type=NoteType.TAP),
            Note(beat=Beat(34,4), column=2, note_type=NoteType.TAP),
            Note(beat=Beat(35,4), column=3, note_type=NoteType.TAP),
            Note(beat=Beat(36,4), column=1, note_type=NoteType.TAP),
            Note(beat=Beat(37,4), column=2, note_type=NoteType.TAP),
            Note(beat=Beat(38,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(38,4), column=1, note_type=NoteType.TAP),
            Note(beat=Beat(39,4), column=3, note_type=NoteType.TAP),
            Note(beat=Beat(40,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(41,4), column=1, note_type=NoteType.TAP),
            Note(beat=Beat(41,4), column=3, note_type=NoteType.TAP),
            Note(beat=Beat(42,4), column=1, note_type=NoteType.LIFT),
            Note(beat=Beat(42,4), column=3, note_type=NoteType.LIFT),
            Note(beat=Beat(44,4), column=0, note_type=NoteType.ROLL_HEAD),
            Note(beat=Beat(45,4), column=3, note_type=NoteType.ROLL_HEAD),
            Note(beat=Beat(48,4), column=0, note_type=NoteType.TAIL),
            Note(beat=Beat(48,4), column=1, note_type=NoteType.MINE),
            Note(beat=Beat(48,4), column=2, note_type=NoteType.MINE),
            Note(beat=Beat(48,4), column=3, note_type=NoteType.TAIL),
        ], notes)

    def test_handles_whitespace(self):
        chart = testing_chart()
        chart.notes = indent(chart.notes, '     ')
        first_3_notes = list(NoteData.from_chart(chart))[:3]
        
        self.assertListEqual([
            Note(beat=Beat(16,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(18,4), column=2, note_type=NoteType.TAP),
            Note(beat=Beat(20,4), column=1, note_type=NoteType.HOLD_HEAD),
        ], first_3_notes)
    
    def test_handles_notes2(self):
        # turn testing_chart() into an SSC chart
        chart = SSCChart.blank()
        chart.update(testing_chart())
        
        notes = list(NoteData.from_chart(chart))
        chart['NOTES2'] = chart.notes
        del chart.notes
        notes2 = list(NoteData.from_chart(chart))

        self.assertEqual(notes, notes2)