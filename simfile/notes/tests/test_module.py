from textwrap import indent
import unittest

from .helpers import *
from .. import *
from ... import open as open_simfile
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
        l9 = open_simfile('testdata/L9.ssc')
        chart = l9.charts[0]
        
        notes = list(NoteData.from_chart(chart))
        self.assertListEqual([
            Note(beat=Beat(191, 48), column=0, note_type=NoteType.KEYSOUND, keysound_index=6),
            Note(beat=Beat(191, 48), column=1, note_type=NoteType.KEYSOUND, keysound_index=7),
            Note(beat=Beat(191, 48), column=2, note_type=NoteType.KEYSOUND, keysound_index=8),
            Note(beat=Beat(191, 48), column=3, note_type=NoteType.KEYSOUND, keysound_index=4),
            Note(beat=Beat(192, 48), column=0, note_type=NoteType.KEYSOUND, keysound_index=1),
            Note(beat=Beat(192, 48), column=1, note_type=NoteType.KEYSOUND, keysound_index=2),
            Note(beat=Beat(192, 48), column=2, note_type=NoteType.KEYSOUND, keysound_index=3),
            Note(beat=Beat(192, 48), column=3, note_type=NoteType.TAP, keysound_index=0),
            Note(beat=Beat(193, 48), column=0, note_type=NoteType.KEYSOUND, keysound_index=5),
            Note(beat=Beat(204, 48), column=1, note_type=NoteType.TAP, keysound_index=9),
        ], notes[:10])
    
    def test_update_chart_handles_notes2(self):
        l9 = open_simfile('testdata/L9.ssc')
        chart = l9.charts[0]
        notedata = NoteData.from_chart(chart)
        modified_notedata: NoteData = NoteData.from_notes(
            (
                Note(beat=n.beat, column=3-n.column, note_type=n.note_type)
                for n in notedata
            ),
            notedata.columns,
        )
        modified_notedata.update_chart(chart)

        self.assertEqual(chart.notes, str(modified_notedata))
        self.assertIn('NOTES2', chart)
        self.assertNotIn('NOTES', chart)
    
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
    
    def test_from_notes_handles_multiple_players(self):
        notes = [
            Note(beat=Beat(n,3), column=n%4, note_type=NoteType.TAP, player=p)
            for p in range(2) for n in range(12)
        ]
        note_data = NoteData.from_notes(notes, 4)
        notes_from_note_data = list(note_data)
        expected_player_note_data = '1000\n0100\n0010\n0001\n' * 3
        expected_note_data = f'{expected_player_note_data}&\n{expected_player_note_data}'

        self.assertEqual(expected_note_data, str(note_data))
        self.assertEqual(notes, notes_from_note_data)
    
    def test_from_notes_handles_second_player_only(self):
        notes = [
            Note(beat=Beat(n,3), column=n%4, note_type=NoteType.TAP, player=1)
            for n in range(12)
        ]
        note_data = NoteData.from_notes(notes, 4)
        notes_from_note_data = list(note_data)
        expected_note_data = (
            '0000\n0000\n0000\n0000\n' +
            '&\n' +
            '1000\n0100\n0010\n0001\n' * 3
        )
        
        self.assertEqual(expected_note_data, str(note_data))
        self.assertEqual(notes, notes_from_note_data)
    
    def test_from_notes_handles_keysound_indices(self):
        notes = [
            Note(beat=Beat(1), column=1, note_type=NoteType.KEYSOUND, keysound_index=0)
        ] + [
            Note(beat=Beat(4), column=n, note_type=NoteType.TAP, keysound_index=n*5)
            for n in range(4)
        ]
        note_data = NoteData.from_notes(notes, 4)
        notes_from_note_data = list(note_data)
        expected_note_data = (
            '0000\n0K[0]00\n0000\n0000\n'
            ',\n'
            '1[0]1[5]1[10]1[15]\n0000\n0000\n0000\n'
        )

        self.assertEqual(expected_note_data, str(note_data))
        self.assertEqual(notes, notes_from_note_data)