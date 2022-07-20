"""
Union types for simfile & chart classes.
"""
from typing import Union

from .sm import *
from .ssc import *

__all__ = ["Simfile", "Charts", "Chart"]

Simfile = Union[SSCSimfile, SMSimfile]
"""Union of :class:`.SSCSimfile` and :class:`.SMSimfile`."""


Charts = Union[SSCCharts, SMCharts]
"""Union of :class:`.SSCCharts` and :class:`.SMCharts`."""


Chart = Union[SSCChart, SMChart]
"""Union of :class:`.SSCChart` and :class:`.SMChart`."""
