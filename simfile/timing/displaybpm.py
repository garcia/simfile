from decimal import Decimal
from typing import NamedTuple, Union

from . import BeatValues
from ._private.timingsource import timing_source
from ..ssc import SSCChart
from ..types import Simfile


__all__ = [
    'StaticDisplayBPM', 'RangeDisplayBPM', 'RandomDisplayBPM', 'DisplayBPM',
    'displaybpm',
]


class StaticDisplayBPM(NamedTuple):
    """A single BPM value."""
    value: Decimal

    @property
    def min(self) -> Decimal:
        """Returns the single BPM value."""
        return self.value

    @property
    def max(self) -> Decimal:
        """Returns the single BPM value."""
        return self.value
    
    def __str__(self):
        """Returns the rounded BPM value as a string."""
        return str(round(self.value))


class RangeDisplayBPM(NamedTuple):
    """A range of BPM values."""
    min: Decimal
    max: Decimal

    def __str__(self):
        """Returns the rounded min and max values joined by a ":"."""
        return f"{round(self.min)}:{round(self.max)}"


class RandomDisplayBPM(NamedTuple):
    """
    Used by StepMania to obfuscate the displayed BPM with random numbers.
    """
    def __str__(self):
        """Returns an asterisk "*"."""
        return '*'


DisplayBPM = Union[StaticDisplayBPM, RangeDisplayBPM, RandomDisplayBPM]
"""Union of the three DisplayBPM variants above."""


def displaybpm(
    simfile: Simfile,
    ssc_chart: SSCChart = SSCChart()
) -> DisplayBPM:
    """
    Get the display BPM from a simfile and optionally an SSC chart.

    If a DISPLAYBPM property is present, its value is used as follows:

    * One number maps to :class:`StaticDisplayBPM`
    * Two ":"-separated numbers maps to :class:`RangeDisplayBPM`
    * A literal "*" maps to :class:`RandomDisplayBPM`

    Otherwise, the BPMS property will be used. A single BPM maps to
    :class:`StaticDisplayBPM`; if there are multiple, the minimum and
    maximum will be identified and passed to :class:`RangeDisplayBPM`.

    If both an :class:`.SSCSimfile` (version 0.7 or higher) and an
    :class:`.SSCChart` are provided, and if the chart contains any
    timing fields, the chart will be used as the source of timing.
    """
    properties = timing_source(simfile, ssc_chart)
    if 'DISPLAYBPM' in properties:
        displaybpm_value = properties['DISPLAYBPM']
        if displaybpm_value == '*':
            return RandomDisplayBPM()
        elif ':' in displaybpm_value:
            min_bpm, _, max_bpm = displaybpm_value.partition(':')
            return RangeDisplayBPM(min=Decimal(min_bpm), max=Decimal(max_bpm))
        else:
            return StaticDisplayBPM(value=Decimal(displaybpm_value))
    else:
        bpms = [e.value for e in BeatValues.from_str(properties['BPMS'])]
        if len(bpms) == 1:
            return StaticDisplayBPM(bpms[0])
        else:
            return RangeDisplayBPM(min=min(bpms), max=max(bpms))
