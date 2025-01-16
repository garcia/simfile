from collections import defaultdict
from typing import Optional, Union

from simfile.sm import SMChart
from simfile.ssc import AttachedSSCChart, SSCSimfile, SSCChart
from simfile.types import AttachedChart, Simfile, Chart


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
    SSCChart.offset,
)

CHART_TIMING_DEFAULTS = {
    SSCChart.bpms: "0.000=60.000",
    SSCChart.stops: "",
    SSCChart.delays: "",
    SSCChart.timesignatures: "0.000=4=4",
    SSCChart.tickcounts: "0.000=4",
    SSCChart.combos: "0.000=1",
    SSCChart.warps: "",
    SSCChart.speeds: "0.000=1.000=0.000=0",
    SSCChart.scrolls: "0.000=1.000",
    SSCChart.fakes: "",
    SSCChart.labels: "0.000=Song Start",
    SSCChart.offset: "0.000",
}


def timing_source(
    source: Union[Simfile, AttachedChart]
) -> Union[Simfile, AttachedSSCChart]:
    if isinstance(source, Simfile):
        return source
    elif (
        isinstance(source, AttachedSSCChart)
        and float(source._simfile.version or "0") >= SSC_VERSION_SPLIT_TIMING
        and any(timing_prop.__get__(source) for timing_prop in CHART_TIMING_PROPERTIES)
    ):
        return source
    else:
        return source._simfile
