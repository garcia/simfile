from typing import Union

from .sm import *
from .ssc import *

__all__ = ['Simfile', 'Charts', 'Chart']

Simfile = Union[SSCSimfile, SMSimfile]
"""
Union of :class:`simfile.ssc.SSCSimfile` and :class:`simfile.sm.SMSimfile`.
"""


Charts = Union[SSCCharts, SMCharts]
"""
Union of :class:`simfile.ssc.SSCCharts` and :class:`simfile.sm.SMCharts`.
"""


Chart = Union[SSCChart, SMChart]
"""
Union of :class:`simfile.ssc.SSCChart` and :class:`simfile.sm.SMChart`.
"""
