from simfile.ssc import SSCChart
from textwrap import indent
import unittest

from .helpers import *
from .. import *
from ...timing import Beat


class TestNoteData(unittest.TestCase):
    def test_iter(self):
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

    def test_iter_handles_whitespace(self):
        chart = testing_chart()
        chart.notes = indent(chart.notes, '     ')
        notedata = NoteData.from_chart(chart)
        first_3_notes = list(notedata)[:3]
        
        self.assertListEqual([
            Note(beat=Beat(16,4), column=0, note_type=NoteType.TAP),
            Note(beat=Beat(18,4), column=2, note_type=NoteType.TAP),
            Note(beat=Beat(20,4), column=1, note_type=NoteType.HOLD_HEAD),
        ], first_3_notes)
    
    def test_iter_handles_routine_chart(self):
        chart = testing_chart()
        chart.notes = f'{chart.notes}\n&\n{chart.notes}'
        notedata = NoteData.from_chart(chart)
        notes = list(notedata)
        first_half = notes[:len(notes)]
        second_half = notes[len(notes):]

        # since we copied the chart for both players, check that every field
        # matches except for the player
        for note1, note2 in zip(first_half, second_half):
            self.assertEqual(note1.beat, note2.beat)
            self.assertEqual(note1.column, note2.column)
            self.assertEqual(note1.note_type, note2.note_type)
            self.assertEqual(note1.player, 0)
            self.assertEqual(note2.player, 1)
    
    def test_from_chart_and_iter_handle_notes2(self):
        # turn testing_chart() into an SSC chart
        chart = SSCChart.blank()
        chart.update(testing_chart())
        
        notes = list(NoteData.from_chart(chart))
        chart['NOTES2'] = chart.notes
        del chart.notes
        notes2 = list(NoteData.from_chart(chart))

        self.assertEqual(notes, notes2)
    
    def test_from_notes(self):
        note_data = NoteData.from_chart(testing_chart())
        note_data_from_notes = NoteData.from_notes(note_data, 4)
        self.assertEqual(str(note_data).strip(), str(note_data_from_notes).strip())
        self.assertListEqual(list(note_data), list(note_data_from_notes))

    def test_from_notes_and_iter_handle_triplets(self):
        notes = [
            Note(beat=Beat(n,3), column=n%4, note_type=NoteType.TAP)
            for n in range(12)
        ]
        note_data = NoteData.from_notes(notes, 4)
        notes_from_note_data = list(note_data)
        
        self.assertEqual('1000\n0100\n0010\n0001\n' * 3, str(note_data))
        self.assertEqual(notes, notes_from_note_data)