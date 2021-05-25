from collections import ChainMap, defaultdict
from typing import DefaultDict

from simfile.ssc import SSCSimfile, SSCChart
from simfile.types import Simfile


# fun fact: SSC versions are stored as floats internally
# this is widely regarded as a mistake, but it does make comparisons easy!
SSC_VERSION_SPLIT_TIMING = 0.7


def ssc_proxy(simfile: Simfile, ssc_chart: SSCChart) -> DefaultDict[str, str]:
    chain = ChainMap(simfile)
    
    if (isinstance(simfile, SSCSimfile) and
        float(simfile.version) >= SSC_VERSION_SPLIT_TIMING):
        chain = chain.new_child(ssc_chart)
    
    return defaultdict(lambda: '', chain)
