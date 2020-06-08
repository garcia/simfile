from decimal import Decimal
from fractions import Fraction, gcd

from .abstract import *


def _lcm(*numbers):
    def lcm(a, b):
        return (a * b) // reduce(gcd, (a, b))
    return reduce(lcm, numbers, 1)


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


class Timing(MSDParameterEncodable, ListWithRepr):
    """
    The Timing class provides sequential access to BPMS and STOPS parameters as
    a list of [beat, value] lists.

    The sole constructor argument should be a string of BPM or stop values.
    """
    def __init__(self, tdata):
        if isinstance(tdata, Timing):
            self.__init__(list(tdata.to_msd_values())[0])
        elif isinstance(tdata, str):
            tlist = []
            for tline in tdata.split(','):
                t = tline.strip().split('=')
                if ''.join(t):
                    tlist.append([decimal_to_192nd(t[0]), Decimal(t[1])])
            self.extend(tlist)
        else:
            raise TypeError('Timing.__init__ expects str or Timing')

    def to_msd_values(self):
        yield ',\n'.join(
            '='.join((str(decimal_from_192nd(t[0])), str(t[1])))
            for t in self)
    
    @classmethod
    def from_msd_values(cls, msd):
        return cls(msd[0])
