from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from simfile.types import Simfile, Chart
from typing import Dict, List, Optional, Type, TypeVar, Union
from .sm import SMChart, SMSimfile
from .ssc import SSCChart, SSCSimfile


__all__ = [
    'InvalidProperty', 'InvalidPropertyBehavior', 'InvalidPropertyException',
    'sm_to_ssc', 'ssc_to_sm',
]


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


class InvalidProperty(Enum):
    MUST_IGNORE = 1
    METADATA = 2
    FILE_REFERENCE = 3
    GAMEPLAY_EVENT = 4
    TIMING_DATA = 5


TYPE_TO_INVALID_PROPERTIES: Dict[Type, Dict[InvalidProperty, List[str]]] = {
    SMSimfile: {
        InvalidProperty.MUST_IGNORE: ['VERSION'],
        InvalidProperty.METADATA: ['ORIGIN', 'TIMESIGNATURES', 'LABELS'],
        InvalidProperty.FILE_REFERENCE: [
            'PREVIEWVID', 'JACKET', 'CDIMAGE', 'DISCIMAGE',
        ],
        InvalidProperty.GAMEPLAY_EVENT: [
            'TICKCOUNTS', 'COMBOS', 'SPEEDS', 'SCROLLS', 'FAKES',
        ],
        InvalidProperty.TIMING_DATA: ['DELAYS', 'WARPS'],
    },
    SMChart: {
        InvalidProperty.METADATA: [
            'CHARTNAME', 'CHARTSTYLE', 'CREDIT', 'DISPLAYBPM',
            'TIMESIGNATURES', 'LABELS',
        ],
        InvalidProperty.GAMEPLAY_EVENT: [
            'TICKCOUNTS', 'COMBOS', 'SPEEDS', 'SCROLLS', 'FAKES',
        ],
        InvalidProperty.TIMING_DATA: [
            'OFFSET', 'BPMS', 'STOPS', 'DELAYS', 'WARPS',
        ],
    },
}


class InvalidPropertyBehavior(Enum):
    COPY_ANYWAY = 1
    IGNORE = 2
    ERROR_IF_VALUE = 3
    ERROR_IF_PRESENT = 4


InvalidPropertyBehaviorMapping = Dict[InvalidProperty, InvalidPropertyBehavior]


INVALID_PROPERTY_BEHAVIORS: InvalidPropertyBehaviorMapping = {
    InvalidProperty.MUST_IGNORE: InvalidPropertyBehavior.IGNORE,
    InvalidProperty.METADATA: InvalidPropertyBehavior.IGNORE,
    InvalidProperty.FILE_REFERENCE: InvalidPropertyBehavior.IGNORE,
    InvalidProperty.GAMEPLAY_EVENT: InvalidPropertyBehavior.ERROR_IF_VALUE,
    InvalidProperty.TIMING_DATA: InvalidPropertyBehavior.ERROR_IF_PRESENT,
}


class InvalidPropertyException(Exception):
    # TODO: human-friendly string
    pass


_CONVERT_TYPE = TypeVar(
    '_CONVERT_TYPE', SMSimfile, SSCSimfile, SMChart, SSCChart, Simfile, Chart,
)
_CONVERT_SIMFILE = TypeVar('_CONVERT_SIMFILE', SMSimfile, SSCSimfile)
_CONVERT_CHART = TypeVar('_CONVERT_CHART', SMChart, SSCChart)

def _blank(t: Type[_CONVERT_TYPE]) -> _CONVERT_TYPE:
    return t(string=TYPE_TO_BLANK_DATA[t])


def _should_copy_property(
    property: str,
    value: str,
    invalid_properties: Dict[InvalidProperty, List[str]],
    invalid_property_behaviors: InvalidPropertyBehaviorMapping
) -> bool:
    for invalid_property, properties in invalid_properties.items():
        if property in properties:
            behavior = invalid_property_behaviors.get(invalid_property) \
                or INVALID_PROPERTY_BEHAVIORS[invalid_property]
            if behavior == InvalidPropertyBehavior.COPY_ANYWAY:
                return True
            if behavior == InvalidPropertyBehavior.IGNORE:
                return False
            if behavior == InvalidPropertyBehavior.ERROR_IF_PRESENT:
                if not value.strip():
                    return False
            raise InvalidPropertyException(
                invalid_property,
                property,
            )
    return True


def _copy_properties(
    source: _CONVERT_TYPE,
    output: _CONVERT_TYPE,
    output_type: Type[_CONVERT_TYPE],
    invalid_property_behaviors: InvalidPropertyBehaviorMapping,
) -> None:
    invalid_properties = TYPE_TO_INVALID_PROPERTIES.get(output_type, {})
    for property, value in source.items():
        if _should_copy_property(
            property,
            value,
            invalid_properties,
            invalid_property_behaviors,
        ):
            output[property] = value


def _convert(
    simfile: Simfile,
    output_simfile_type: Type[_CONVERT_SIMFILE],
    output_chart_type: Type[_CONVERT_CHART],
    simfile_template: Optional[_CONVERT_SIMFILE] = None,
    chart_template: Optional[_CONVERT_CHART] = None,
    invalid_property_behaviors: InvalidPropertyBehaviorMapping = {}
) -> _CONVERT_SIMFILE:
    output_simfile = deepcopy(simfile_template) or _blank(output_simfile_type)

    _copy_properties(
        source=simfile,
        output=output_simfile,
        output_type=output_simfile_type,
        invalid_property_behaviors=invalid_property_behaviors,
    )
    
    for _chart in simfile.charts:
        chart: Chart = _chart # typing workaround
        output_chart = deepcopy(chart_template) or _blank(output_chart_type)
        if isinstance(chart, SMSimfile):
            output_chart.stepstype = chart.stepstype
            output_chart.description = chart.description
            output_chart.difficulty = chart.difficulty
            output_chart.meter = chart.meter
            output_chart.radarvalues = chart.radarvalues
            output_chart.notes = chart.notes
        else:
            _copy_properties(
                source=chart,
                output=output_chart,
                output_type=output_chart_type,
                invalid_property_behaviors=invalid_property_behaviors,
            )
        output_simfile.charts.append(output_chart)
    
    return output_simfile


def sm_to_ssc(
    sm_simfile: SMSimfile,
    *,
    simfile_template: Optional[SSCSimfile] = None,
    chart_template: Optional[SSCChart] = None,
    invalid_property_behaviors: InvalidPropertyBehaviorMapping = {},
) -> SSCSimfile:
    return _convert(
        simfile=sm_simfile,
        output_simfile_type=SSCSimfile,
        output_chart_type=SSCChart,
        simfile_template=simfile_template,
        chart_template=chart_template,
        invalid_property_behaviors=invalid_property_behaviors,
    )


def ssc_to_sm(
    ssc_simfile: SSCSimfile,
    *,
    simfile_template: Optional[SMSimfile] = None,
    chart_template: Optional[SMChart] = None,
    invalid_property_behaviors: InvalidPropertyBehaviorMapping = {},
) -> SMSimfile:
    return _convert(
        simfile=ssc_simfile,
        output_simfile_type=SMSimfile,
        output_chart_type=SMChart,
        simfile_template=simfile_template,
        chart_template=chart_template,
        invalid_property_behaviors=invalid_property_behaviors,
    )