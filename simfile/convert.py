"""
Functions for converting SM to SSC simfiles and vice-versa.
"""
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from simfile.types import Simfile, Chart
from typing import DefaultDict, Dict, List, Optional, Type, TypeVar
from .sm import SMChart, SMSimfile
from .ssc import SSCChart, SSCSimfile


__all__ = [
    'KnownProperty', 'InvalidPropertyBehavior', 'InvalidPropertyException',
    'sm_to_ssc', 'ssc_to_sm',
]


DEFAULT_PROPERTIES: DefaultDict[str, str] = defaultdict(lambda: '', {
    'TIMESIGNATURES': '0.000=4=4',
    'TICKCOUNTS': '0.000=4',
    'COMBOS': '0.000=1',
    'SPEEDS': '0.000=1.000=0.000=0',
    'SCROLLS': '0.000=1.000',
    'LABELS': '0.000=Song Start',
})


class KnownProperty(Enum):
    """
    Types of known properties.

    These mirror the lists of known properties documented in
    :class:`.BaseSimfile` and :class:`.SSCSimfile`.
    """
    SSC_VERSION = 1
    METADATA = 2
    FILE_PATH = 3
    GAMEPLAY_EVENT = 4
    TIMING_DATA = 5


INVALID_PROPERTIES: Dict[Type, Dict[KnownProperty, List[str]]] = {
    SMSimfile: {
        KnownProperty.SSC_VERSION: ['VERSION'],
        KnownProperty.METADATA: ['ORIGIN', 'TIMESIGNATURES', 'LABELS'],
        KnownProperty.FILE_PATH: [
            'PREVIEWVID', 'JACKET', 'CDIMAGE', 'DISCIMAGE',
        ],
        KnownProperty.GAMEPLAY_EVENT: [
            'TICKCOUNTS', 'COMBOS', 'SPEEDS', 'SCROLLS', 'FAKES',
        ],
        KnownProperty.TIMING_DATA: ['DELAYS', 'WARPS'],
    },
    SMChart: {
        KnownProperty.METADATA: [
            'CHARTNAME', 'CHARTSTYLE', 'CREDIT', 'DISPLAYBPM',
            'TIMESIGNATURES', 'LABELS',
        ],
        KnownProperty.GAMEPLAY_EVENT: [
            'TICKCOUNTS', 'COMBOS', 'SPEEDS', 'SCROLLS', 'FAKES',
        ],
        KnownProperty.TIMING_DATA: [
            'OFFSET', 'BPMS', 'STOPS', 'DELAYS', 'WARPS',
        ],
    },
}


class InvalidPropertyBehavior(Enum):
    """
    How to handle an invalid property during conversion.

    If a known property can't be converted to the destination type...

    * `COPY_ANYWAY`: copy the property regardless
    * `IGNORE`: do not copy the property
    * `ERROR_UNLESS_DEFAULT`: raise :class:`InvalidPropertyException`
      unless its value is the default value
    * `ERROR`: raise :class:`InvalidPropertyException` regardless of
      the property's value

    The "default value" for most properties is an empty string. If the
    destination type's :code:`.blank` output has a non-empty value for
    the property, that value is considered the default instead (except
    for `BPMS`).
    """
    COPY_ANYWAY = 1
    IGNORE = 2
    ERROR_UNLESS_DEFAULT = 3
    ERROR = 4


InvalidPropertyBehaviorMapping = Dict[KnownProperty, InvalidPropertyBehavior]


INVALID_PROPERTY_BEHAVIORS: InvalidPropertyBehaviorMapping = {
    KnownProperty.SSC_VERSION: InvalidPropertyBehavior.IGNORE,
    KnownProperty.METADATA: InvalidPropertyBehavior.IGNORE,
    KnownProperty.FILE_PATH: InvalidPropertyBehavior.IGNORE,
    KnownProperty.GAMEPLAY_EVENT: InvalidPropertyBehavior.ERROR_UNLESS_DEFAULT,
    KnownProperty.TIMING_DATA: InvalidPropertyBehavior.ERROR,
}


class InvalidPropertyException(Exception):
    """
    Raised by conversion functions if a property cannot be converted.
    """
    # TODO: human-friendly string
    pass


_CONVERT_TYPE = TypeVar(
    '_CONVERT_TYPE', SMSimfile, SSCSimfile, SMChart, SSCChart, Simfile, Chart,
)
_CONVERT_SIMFILE = TypeVar('_CONVERT_SIMFILE', SMSimfile, SSCSimfile)
_CONVERT_CHART = TypeVar('_CONVERT_CHART', SMChart, SSCChart)


def _should_copy_property(
    property: str,
    value: str,
    invalid_properties: Dict[KnownProperty, List[str]],
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
            if behavior == InvalidPropertyBehavior.ERROR_UNLESS_DEFAULT:
                if value.strip() != DEFAULT_PROPERTIES[property]:
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
    invalid_properties = INVALID_PROPERTIES.get(output_type, {})
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
    output_simfile = deepcopy(simfile_template) or output_simfile_type.blank()

    _copy_properties(
        source=simfile,
        output=output_simfile,
        output_type=output_simfile_type,
        invalid_property_behaviors=invalid_property_behaviors,
    )
    
    for _chart in simfile.charts:
        chart: Chart = _chart # typing workaround
        output_chart = deepcopy(chart_template) or output_chart_type.blank()
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
) -> SSCSimfile:
    """
    Convert an SM simfile to an equivalent SSC simfile.

    `simfile_template` and `chart_template` can optionally be provided
    to define the initial simfile and chart prior to copying properties
    from the source object. If they are not provided,
    :meth:`.SMSimfile.blank` and :meth:`.SMChart.blank` will supply the
    template objects.
    """
    return _convert(
        simfile=sm_simfile,
        output_simfile_type=SSCSimfile,
        output_chart_type=SSCChart,
        simfile_template=simfile_template,
        chart_template=chart_template,
        invalid_property_behaviors={},
    )


def ssc_to_sm(
    ssc_simfile: SSCSimfile,
    *,
    simfile_template: Optional[SMSimfile] = None,
    chart_template: Optional[SMChart] = None,
    invalid_property_behaviors: InvalidPropertyBehaviorMapping = {},
) -> SMSimfile: 
    """
    Convert an SSC simfile to an equivalent SM simfile.

    `simfile_template` and `chart_template` can optionally be provided
    to define the initial simfile and chart prior to copying properties
    from the source object. If they are not provided,
    :meth:`.SSCSimfile.blank` and :meth:`.SSCChart.blank` will supply
    the template objects.

    Not all SSC properties are valid for SM simfiles, and some of these
    properties may be crucial for the simfile to behave as intended
    during gameplay. By default, invalid properties are ignored unless:

    * The property is a gameplay event and has a non-default value, or
    * The property contains timing data.

    These behaviors can be overridden by supplying the
    `invalid_property_behaviors` parameter, which maps
    :class:`KnownProperty` to :class:`InvalidPropertyBehavior` values.
    This mapping need not cover every :class:`KnownProperty`; any
    missing values will fall back to the default mapping described
    above.
    """
    return _convert(
        simfile=ssc_simfile,
        output_simfile_type=SMSimfile,
        output_chart_type=SMChart,
        simfile_template=simfile_template,
        chart_template=chart_template,
        invalid_property_behaviors=invalid_property_behaviors,
    )