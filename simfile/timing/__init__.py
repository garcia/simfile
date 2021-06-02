from decimal import Decimal
from fractions import Fraction
from numbers import Rational
from simfile.ssc import SSCChart
from typing import Optional, Type, NamedTuple

from ._private.sscproxy import ssc_proxy
from simfile._private.generic import ListWithRepr
from simfile.types import Simfile, Chart


__all__ = ['Beat', 'BeatValue', 'BeatValues', 'TimingData']


MEASURE_SUBDIVISION = 192
BEAT_SUBDIVISION = MEASURE_SUBDIVISION // 4


class Beat(Fraction):
    """
    A fractional beat value, denoting vertical position in a simfile.

    The constructor the same arguments as Python's :code:`Fraction`. If
    the input doesn't have an explicit denominator (either as a
    `denominator` argument or a lone rational argument), the resulting
    fraction will be rounded to the nearest :meth:`tick`.
    """
    def __new__(cls, numerator=0, denominator=None):
        self = super().__new__(cls, numerator, denominator)
        if denominator or isinstance(numerator, Rational):
            return self
        else:
            return self.round_to_tick()

    @classmethod
    def tick(cls) -> 'Beat':
        """
        1/48 of a beat (1/192 of a measure).
        """
        return cls(1, BEAT_SUBDIVISION)
    
    @classmethod
    def from_str(cls, beat_str) -> 'Beat':
        """
        Convert a decimal string to a beat, rounding to the nearest tick.
        """
        return Beat(beat_str).round_to_tick()
    
    def round_to_tick(self) -> 'Beat':
        """
        Round the beat to the nearest tick.
        """
        return Beat(int(round(self * BEAT_SUBDIVISION)), BEAT_SUBDIVISION)
    
    def __str__(self) -> str:
        """
        Convert the beat to its usual MSD representation (3 decimal digits).
        """
        return f'{float(self):.3f}'
    
    def __repr__(self) -> str:
        """
        Pretty repr() for beats.

        If the beat falls on a tick, the printed value is a decimal
        representation with at most 3 decimal digits and no trailing
        zeros. Otherwise, the printed value is the numerator and
        denominator.
        """
        if BEAT_SUBDIVISION % self.denominator == 0:
            return f"Beat({str(self).rstrip('0').rstrip('.')})"
        else:
            return super().__repr__()

    # Preserve type for methods inherited from Fraction

    def __abs__(self): return Beat(super().__abs__())
    def __add__(self, other): return Beat(super().__add__(other))
    def __divmod__(self, other):
        quotient, remainder = super().__divmod__(other)
        return (quotient, Beat(remainder))
    def __mod__(self, other): return Beat(super().__mod__(other))
    def __mul__(self, other): return Beat(super().__mul__(other))
    def __neg__(self): return Beat(super().__neg__())
    def __pos__(self): return Beat(super().__pos__())
    def __pow__(self, other): return Beat(super().__pow__(other))
    def __radd__(self, other): return Beat(super().__radd__(other))
    def __rdivmod__(self, other):
        quotient, remainder = super().__rdivmod__(other)
        return (quotient, Beat(remainder))
    def __rmod__(self, other): return Beat(super().__rmod__(other))
    def __rmul__(self, other): return Beat(super().__rmul__(other))
    def __rpow__(self, other): return Beat(super().__rpow__(other))
    def __rsub__(self, other): return Beat(super().__rsub__(other))
    def __rtruediv__(self, other): return Beat(super().__rtruediv__(other))
    def __sub__(self, other): return Beat(super().__sub__(other))
    def __truediv__(self, other): return Beat(super().__truediv__(other))
    def limit_denominator(self, max_denominator=1000000):
        return Beat(super().limit_denominator(max_denominator))


class BeatValue(NamedTuple):
    """
    An event that occurs on a particular beat, e.g. a BPM change or stop.

    The decimal value's semantics vary based on the type of event:
    
    * BPMS: the new BPM value
    * STOPS, DELAYS: number of seconds to pause
    * WARPS: number of beats to skip
    """
    beat: Beat
    value: Decimal


class BeatValues(ListWithRepr[BeatValue]):
    """
    A list of :class:`BeatValue` instances.
    """
    @classmethod
    def from_str(cls: Type['BeatValues'], string: str) -> 'BeatValues':
        """
        Parse the MSD value component of a timing data list.

        Specifically, `BPMS`, `STOPS`, `DELAYS`, and `WARPS` are
        the timing data lists whose values can be parsed by this
        method.
        """
        instance = cls()
        
        if string.strip():
            for row in string.split(','):
                beat, value = row.strip().split('=')
                instance.append(BeatValue(Beat.from_str(beat), Decimal(value)))
        
        return instance

    def __str__(self) -> str:
        """
        Convert the beat-value pairs to their MSD value representation.
        """
        return ',\n'.join(f'{event.beat}={event.value}' for event in self)


class TimingData(NamedTuple):
    """
    Timing data for a simfile, possibly enriched with SSC chart timing.
    """
    bpms: BeatValues
    stops: BeatValues
    delays: BeatValues
    warps: BeatValues
    offset: Decimal

    @classmethod
    def from_simfile(
        cls: Type['TimingData'],
        simfile: Simfile,
        chart: Optional[Chart] = None
    ) -> 'TimingData':
        """
        Obtain timing data from a simfile and optionally an SSC chart.

        If both an :class:`.SSCSimfile` (version 0.7 or higher) and an
        :class:`.SSCChart` are provided, any "split timing" defined in
        the chart will take precedence over the simfile's timing data.
        This is true regardless of the property's value; for example, a
        blank `STOPS` value in the chart overrides a non-blank value
        from the simfile.

        Per StepMania's behavior, the offset defaults to zero if the
        simfile (and/or SSC chart) doesn't specify one. (However,
        unlike StepMania, the BPM does not default to 60 when omitted;
        the default BPM doesn't appear to be used deliberately in any
        existing simfiles, whereas the default offset does get used
        intentionally from time to time.)
        """
        properties = ssc_proxy(simfile, chart)
        return TimingData(
            bpms=BeatValues.from_str(properties['BPMS']),
            stops=BeatValues.from_str(properties['STOPS']),
            delays=BeatValues.from_str(properties['DELAYS']),
            warps=BeatValues.from_str(properties['WARPS']),
            offset=Decimal(properties['OFFSET'] or 0),
        )