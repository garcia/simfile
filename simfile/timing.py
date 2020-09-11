from collections import UserList
from decimal import Decimal
from fractions import Fraction


__all__ = ['Timing']


def decimal_to_192nd(dec):
    """
    Convert a decimal value to a fraction whose denominator is 192.
    """
    return Fraction(int(round(Decimal(dec) * 192)), 192)


def decimal_from_192nd(frac):
    """
    Convert a fraction to a decimal value quantized to 1/1000.
    """
    return Decimal(float(frac)).quantize(Decimal('0.001'))


class Timing(UserList):
    """
    The Timing class provides sequential access to BPMS and STOPS parameters as
    a list of (beat, value) tuples.

    The sole constructor argument should be a string of BPM or stop values.
    """
    def __init__(self, string: str):
        for row in string.split(','):
            beat, value = row.strip().split('=')
            self.append((decimal_to_192nd(beat), Decimal(value)))

    def __str__(self):
        return ',\n'.join(f'{decimal_from_192nd(beat)}:{value}'
            for (beat, value) in self)
