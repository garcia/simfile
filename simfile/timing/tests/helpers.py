from simfile.sm import SMSimfile


def testing_simfile():
    return SMSimfile(string=
        '#BPMS:0.000=120.000,\n'
        '1.000=150.000,\n'
        '2.000=200.000,\n'
        '3.000=300.000;\n'
        '#STOPS:2.500=0.500,\n'
        '3.000=0.100;\n'
        '#OFFSET:-0.009;\n'
    )
