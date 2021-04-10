from decimal import Decimal
from fractions import Fraction
import unittest

from ..notes import *
from ..timing import Beat
from ..sm import SMSimfile, SMChart


def testing_simfile():
    return SMSimfile(string=
        '#BPMS:0.000=60.000,\n'
        '4.000=120.000;\n'
        '#STOPS:6.000=1.000;\n'
        '#OFFSET:0.000;\n'
    )


def testing_chart():
    return SMChart(
        '\n'
        '     dance-single:\n'
        '     Brackets:\n'
        '     Edit:\n'
        '     12:\n'
        '     0.793,1.205,0.500,0.298,0.961:\n'
        '0000\n'
        '0000\n'
        '0000\n'
        '0000\n'
        ',\n'
        '1000 \n'
        '0010\n'
        '0200\n'
        '0001\n'
        '0310\n'
        '0000\n'
        '1001\n'
        '0MM0\n'
        ',\n'
        '1000\n'
        '0100\n'
        '0010\n'
        '0001\n'
        '0100\n'
        '0010\n'
        '1100\n'
        '0001\n'
        '1000\n'
        '0101\n'
        '0L0L\n'
        '0000\n'
        '4000\n'
        '0004\n'
        '0000\n'
        '0000\n'
        ',\n'
        '3MM3\n'
        '0000\n'
        '0000\n'
        '0000\n'
    )


class TestNoteStream(unittest.TestCase):
    def test_from_str(self):
        notes = list(NoteStream.from_chart(testing_chart()))
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


class TestNoteCounter(unittest.TestCase):
    def test_add_chart(self):
        nc = NoteCounter()
        nc.add_chart(testing_chart())
        self.assertEqual(19, nc.count)
    
    def test_count_jumps_once_false(self):
        nc = NoteCounter(count_jumps_once=False)
        nc.add_chart(testing_chart())
        self.assertEqual(23, nc.count)
    
    def test_add_chart_multiple_calls(self):
        nc = NoteCounter()
        nc.add_chart(testing_chart())
        nc.add_chart(testing_chart())
        self.assertEqual(38, nc.count)