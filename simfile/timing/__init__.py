from decimal import Decimal
from fractions import Fraction
from simfile.ssc import SSCChart
from typing import Type, NamedTuple

from ._private.sscproxy import ssc_proxy
from simfile._private.generic import ListWithRepr
from simfile.types import Simfile


__all__ = ['Beat', 'BeatValue', 'BeatValues', 'TimingData']


MEASURE_SUBDIVISION = 192
BEAT_SUBDIVISION = MEASURE_SUBDIVISION // 4


class Beat(Fraction):
    """
    A fractional beat value, denoting vertical position in a simfile.
    """

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
    
    def __str__(self):
        """
        Convert the beat to a string with 3 decimal digits.
        """
        return f'{float(self):.3f}'
    
    def __repr__(self):
        """
        Pretty repr() for beats.

        Includes the string representation with at most 3 decimal
        digits, with trailing zeros removed.
        """
        return f"<Beat {str(self).rstrip('0').rstrip('.')}>"


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

    def serialize(self) -> str:
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
        ssc_chart: SSCChart = SSCChart()
    ) -> 'TimingData':
        """
        Obtain timing data from a simfile and optionally an SSC chart.

        If an SSC chart is provided, any timing data properties it
        contains will take precedence over the simfile's timing data.
        This is true regardless of the property's value; for example, a
        blank `STOPS` value in the SSC chart overrides a non-blank
        value from the simfile.
        """
        properties = ssc_proxy(simfile, ssc_chart)
        return TimingData(
            bpms=BeatValues.from_str(properties['BPMS']),
            stops=BeatValues.from_str(properties['STOPS']),
            delays=BeatValues.from_str(properties['DELAYS']),
            warps=BeatValues.from_str(properties['WARPS']),
            offset=Decimal(properties['OFFSET']),
        )