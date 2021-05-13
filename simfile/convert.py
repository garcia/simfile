from collections import OrderedDict
from copy import deepcopy
from simfile.types import Simfile, Chart
from typing import Dict, Optional, Type, TypeVar, Union
from .sm import SMChart, SMSimfile
from .ssc import SSCChart, SSCSimfile


__all__ = ['sm_to_ssc', 'ssc_to_sm']


TYPE_TO_BLANK_DATA: Dict[Type, str] = {
    SMSimfile: """
#TITLE:;
#SUBTITLE:;
#ARTIST:;
#TITLETRANSLIT:;
#SUBTITLETRANSLIT:;
#ARTISTTRANSLIT:;
#GENRE:;
#CREDIT:;
#BANNER:;
#BACKGROUND:;
#LYRICSPATH:;
#CDTITLE:;
#MUSIC:;
#OFFSET:0.000000;
#SAMPLESTART:100.000000;
#SAMPLELENGTH:12.000000;
#SELECTABLE:YES;
#BPMS:0.000000=60.000000;
#STOPS:;
#BGCHANGES:;
#KEYSOUNDS:;
#ATTACKS:;
    """.strip(),
    SMChart: """
#NOTES:
    :
    :
    :
    1:
    0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
0000
0000
0000
0000
;
    """.strip(),
    SSCSimfile: """
#VERSION:0.83;
#TITLE:;
#SUBTITLE:;
#ARTIST:;
#TITLETRANSLIT:;
#SUBTITLETRANSLIT:;
#ARTISTTRANSLIT:;
#GENRE:;
#ORIGIN:;
#CREDIT:;
#BANNER:;
#BACKGROUND:;
#PREVIEWVID:;
#JACKET:;
#CDIMAGE:;
#DISCIMAGE:;
#LYRICSPATH:;
#CDTITLE:;
#MUSIC:;
#OFFSET:0.000000;
#SAMPLESTART:100.000000;
#SAMPLELENGTH:12.000000;
#SELECTABLE:YES;
#BPMS:0.000=60.000;
#STOPS:;
#DELAYS:;
#WARPS:;
#TIMESIGNATURES:0.000=4=4;
#TICKCOUNTS:0.000=4;
#COMBOS:0.000=1;
#SPEEDS:0.000=1.000=0.000=0;
#SCROLLS:0.000=1.000;
#FAKES:;
#LABELS:0.000=Song Start;
#BGCHANGES:;
#KEYSOUNDS:;
#ATTACKS:;
    """.strip(),
    SSCChart: """
#NOTEDATA:;
#CHARTNAME:;
#STEPSTYPE:;
#DESCRIPTION:;
#CHARTSTYLE:;
#DIFFICULTY:;
#METER:1;
#RADARVALUES:0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000;
#CREDIT:;
#NOTES:
0000
0000
0000
0000
;
    """.strip(),
}


_BLANK_TYPE = TypeVar('_BLANK_TYPE', SMSimfile, SSCSimfile, SMChart, SSCChart)
def _blank(t: Type[_BLANK_TYPE]) -> _BLANK_TYPE:
    return t(string=TYPE_TO_BLANK_DATA[t])


_CONVERT_SIMFILE = TypeVar('_CONVERT_SIMFILE', SMSimfile, SSCSimfile)
_CONVERT_CHART = TypeVar('_CONVERT_CHART', SMChart, SSCChart)
def _convert(
    simfile: Simfile,
    output_simfile_type: Type[_CONVERT_SIMFILE],
    output_chart_type: Type[_CONVERT_CHART],
    simfile_template: Optional[_CONVERT_SIMFILE] = None,
    chart_template: Optional[_CONVERT_CHART] = None,
) -> _CONVERT_SIMFILE:
    output = deepcopy(simfile_template) or _blank(output_simfile_type)

    for key, value in simfile.items():
        output[key] = value
    
    for _chart in simfile.charts:
        chart: Chart = _chart # typing workaround
        output_chart = deepcopy(chart_template) or _blank(output_chart_type)
        output_chart.stepstype = chart.stepstype
        output_chart.description = chart.description
        output_chart.difficulty = chart.difficulty
        output_chart.meter = chart.meter
        output_chart.radarvalues = chart.radarvalues
        output_chart.notes = chart.notes
    
    return output


def sm_to_ssc(
    sm_simfile: SMSimfile,
    *,
    simfile_template: Optional[SSCSimfile] = None,
    chart_template: Optional[SSCChart] = None,
) -> SSCSimfile:
    return _convert(
        simfile=sm_simfile,
        output_simfile_type=SSCSimfile,
        output_chart_type=SSCChart,
        simfile_template=simfile_template,
        chart_template=chart_template,
    )


def ssc_to_sm(
    ssc_simfile: SSCSimfile,
    *,
    simfile_template: Optional[SMSimfile] = None,
    chart_template: Optional[SMChart] = None,
) -> SMSimfile:
    return _convert(
        simfile=ssc_simfile,
        output_simfile_type=SMSimfile,
        output_chart_type=SMChart,
        simfile_template=simfile_template,
        chart_template=chart_template,
    )