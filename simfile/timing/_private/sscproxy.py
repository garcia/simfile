from collections import ChainMap, defaultdict
from typing import DefaultDict, Mapping, Optional

from simfile.ssc import SSCSimfile, SSCChart
from simfile.types import Simfile, Chart


# fun fact: SSC versions are stored as floats internally
# this is widely regarded as a mistake, but it does make comparisons easy!
SSC_VERSION_SPLIT_TIMING = 0.7


def ssc_proxy(simfile: Simfile, chart: Optional[Chart]) -> Mapping[str, str]:
    source: Mapping[str, str]

    if (isinstance(simfile, SSCSimfile) and
        isinstance(chart, SSCChart) and
        float(simfile.version) >= SSC_VERSION_SPLIT_TIMING):
        source = ChainMap(chart, simfile)
    else:
        source = simfile
    
    return defaultdict(lambda: '', source)
