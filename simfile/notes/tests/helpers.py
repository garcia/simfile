from simfile.notes import Note, NoteData
from typing import Iterable
from ...sm import SMSimfile, SMChart


def testing_simfile():
    return SMSimfile(string=
        '#BPMS:0.000=60.000,\n'
        '4.000=120.000;\n'
        '#STOPS:6.000=1.000;\n'
        '#OFFSET:0.000;\n'
    )


def testing_chart():
    return SMChart.from_str(
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
        '1000\n'
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


def testing_notes() -> NoteData:
    return NoteData.from_chart(testing_chart())