from typing import Optional, Union

from simfile.ssc import SSCSimfile, SSCChart
from simfile.types import Simfile, Chart


# Fun fact: SSC versions are stored as floats internally
# This is widely regarded as a mistake, but it does make comparisons easy!
SSC_VERSION_SPLIT_TIMING = 0.7

# These are the properties that, if found in an SSC chart, cause the SSC
# chart's timing to be used for all properties
CHART_TIMING_PROPERTIES = (
    SSCChart.bpms,
    SSCChart.stops,
    SSCChart.delays,
    SSCChart.timesignatures,
    SSCChart.tickcounts,
    SSCChart.combos,
    SSCChart.warps,
    SSCChart.speeds,
    SSCChart.scrolls,
    SSCChart.fakes,
    SSCChart.labels,
)

def timing_source(simfile: Simfile, chart: Optional[Chart]) -> Union[Simfile, SSCChart]:
    if (isinstance(simfile, SSCSimfile) and
        isinstance(chart, SSCChart) and
        float(simfile.version) >= SSC_VERSION_SPLIT_TIMING and
        any(timing_prop.__get__(chart) for timing_prop in CHART_TIMING_PROPERTIES)):
        return chart
    else:
        return simfile
