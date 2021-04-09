from typing import Union

from .sm import *
from .ssc import *

__all__ = ['Simfile', 'Charts', 'Chart']

Simfile = Union[SSCSimfile, SMSimfile]
Charts = Union[SSCCharts, SMCharts]
Chart = Union[SSCChart, SMChart]
