from collections import ChainMap, defaultdict
from typing import DefaultDict

from simfile.types import Simfile
from simfile.ssc import SSCChart


def ssc_proxy(simfile: Simfile, ssc_chart: SSCChart) -> DefaultDict[str, str]:
    return defaultdict(lambda: '', ChainMap(ssc_chart, simfile))
