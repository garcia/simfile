from decimal import Decimal
from fractions import Fraction
import unittest

from ..notes import *
from ..timing import Beat
from ..sm import SMChart


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