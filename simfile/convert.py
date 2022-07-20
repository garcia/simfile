"""
Functions for converting SM to SSC simfiles and vice-versa.
"""
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import DefaultDict, Dict, List, Optional, Type, TypeVar, cast

from .sm import SMChart, SMSimfile
from .ssc import SSCChart, SSCSimfile
from .timing import BeatValue, BeatValues
from .types import Simfile, Chart


__all__ = [
    "PropertyType",
    "InvalidPropertyBehavior",
    "InvalidPropertyException",
    "sm_to_ssc",
    "ssc_to_sm",
]


DEFAULT_PROPERTIES: DefaultDict[str, str] = defaultdict(
    lambda: "",
    {
        "TIMESIGNATURES": "0.000=4=4",
        "TICKCOUNTS": "0.000=4",
        "COMBOS": "0.000=1",
        "SPEEDS": "0.000=1.000=0.000=0",
        "SCROLLS": "0.000=1.000",
        "LABELS": "0.000=Song Start",
    },
)


class PropertyType(Enum):
    """
    Types of known properties.

    These roughly mirror the lists of known properties documented in
    :class:`.BaseSimfile` and :class:`.SSCSimfile`.
    """

    SSC_VERSION = 1
    """The SSC version tag."""

    METADATA = 2
    """Properties that don't affect the gameplay."""

    FILE_PATH = 3
    """Properties that reference file paths (e.g. images)."""

    GAMEPLAY_EVENT = 4
    """Properties that affect gameplay in some fashion."""

    TIMING_DATA = 5
    """Properties that influence when notes must be hit."""


INVALID_PROPERTIES: Dict[Type, Dict[PropertyType, List[str]]] = {
    SMSimfile: {
        PropertyType.SSC_VERSION: ["VERSION"],
        PropertyType.METADATA: [
            "ORIGIN",
            "TIMESIGNATURES",
            "LABELS",
            "MUSICLENGTH",
            "LASTSECONDHINT",
        ],
        PropertyType.FILE_PATH: [
            "PREVIEWVID",
            "JACKET",
            "CDIMAGE",
            "DISCIMAGE",
            "PREVIEW",
        ],
        PropertyType.GAMEPLAY_EVENT: [
            "COMBOS",
            "SPEEDS",
            "SCROLLS",
            "FAKES",
        ],
        PropertyType.TIMING_DATA: ["WARPS"],
    },
    SMChart: {
        PropertyType.METADATA: [
            "CHARTNAME",
            "CHARTSTYLE",
            "CREDIT",
            "DISPLAYBPM",
            "TIMESIGNATURES",
            "LABELS",
        ],
        PropertyType.GAMEPLAY_EVENT: [
            "TICKCOUNTS",
            "COMBOS",
            "SPEEDS",
            "SCROLLS",
            "FAKES",
            "ATTACKS",
        ],
        PropertyType.TIMING_DATA: [
            "OFFSET",
            "BPMS",
            "STOPS",
            "DELAYS",
            "WARPS",
        ],
    },
    SSCSimfile: {},
    SSCChart: {},
}


class InvalidPropertyBehavior(Enum):
    """
    How to handle an invalid property during conversion.
    """

    COPY_ANYWAY = 1
    """Copy the property regardless of the destination type."""

    IGNORE = 2
    """Do not copy the property."""

    ERROR_UNLESS_DEFAULT = 3
    """
    Raise :class:`InvalidPropertyException` unless the property's value is
    the default for its field.

    The "default value" for most properties is an empty string. If the
    destination type's :code:`.blank` output has a non-empty value for the
    property, that value is considered the default instead.
    """

    ERROR = 4
    """
    Raise :class:`InvalidPropertyException` regardless of the value.
    """


InvalidPropertyBehaviorMapping = Dict[PropertyType, InvalidPropertyBehavior]


INVALID_PROPERTY_BEHAVIORS: InvalidPropertyBehaviorMapping = {
    PropertyType.SSC_VERSION: InvalidPropertyBehavior.IGNORE,
    PropertyType.METADATA: InvalidPropertyBehavior.IGNORE,
    PropertyType.FILE_PATH: InvalidPropertyBehavior.IGNORE,
    PropertyType.GAMEPLAY_EVENT: InvalidPropertyBehavior.ERROR_UNLESS_DEFAULT,
    PropertyType.TIMING_DATA: InvalidPropertyBehavior.ERROR_UNLESS_DEFAULT,
}


class InvalidPropertyException(Exception):
    """
    Raised by conversion functions if a property cannot be converted.
    """


_CONVERT_TYPE = TypeVar(
    "_CONVERT_TYPE",
    SMSimfile,
    SSCSimfile,
    SMChart,
    SSCChart,
    Simfile,
    Chart,
)
_CONVERT_SIMFILE = TypeVar("_CONVERT_SIMFILE", SMSimfile, SSCSimfile)
_CONVERT_CHART = TypeVar("_CONVERT_CHART", SMChart, SSCChart)


def _should_copy_property(
    property: str,
    value: str,
    invalid_properties: Dict[PropertyType, List[str]],
    invalid_property_behaviors: InvalidPropertyBehaviorMapping,
) -> bool:
    for invalid_property, properties in invalid_properties.items():
        if property in properties:
            behavior = (
                invalid_property_behaviors.get(invalid_property)
                or INVALID_PROPERTY_BEHAVIORS[invalid_property]
            )
            if behavior == InvalidPropertyBehavior.COPY_ANYWAY:
                return True
            if behavior == InvalidPropertyBehavior.IGNORE:
                return False
            if behavior == InvalidPropertyBehavior.ERROR_UNLESS_DEFAULT:
                if value.strip() == DEFAULT_PROPERTIES[property]:
                    return False
            raise InvalidPropertyException(
                f"cannot convert {repr(property)} (value: {repr(value)})"
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


def _convert_warps(source: Simfile, output: Simfile):
    """
    Stub method for warp conversion.

    Currently raises :code:`NotImplementedError` if warp timing is found.
    """
    if isinstance(source, SMSimfile):
        bpms = BeatValues.from_str(source.bpms)
        stops = BeatValues.from_str(source.stops)
        for beat_values in (bpms, stops):
            for _beat_value in beat_values:
                beat_value: BeatValue = _beat_value  # typing workaround
                if beat_value.value < 0:
                    raise NotImplementedError(
                        "Warp timing in SMSimfile can't be converted yet"
                    )
    elif isinstance(source, SSCSimfile):
        if len(BeatValues(source.warps)):
            raise NotImplementedError(
                "Warp timing in SSCSimfile can't be converted yet"
            )


def _convert(
    simfile: Simfile,
    output_simfile_type: Type[_CONVERT_SIMFILE],
    output_chart_type: Type[_CONVERT_CHART],
    simfile_template: Optional[_CONVERT_SIMFILE] = None,
    chart_template: Optional[_CONVERT_CHART] = None,
    invalid_property_behaviors: InvalidPropertyBehaviorMapping = {},
) -> _CONVERT_SIMFILE:
    output_simfile = deepcopy(simfile_template) or output_simfile_type.blank()

    _convert_warps(source=simfile, output=output_simfile)

    _copy_properties(
        source=simfile,
        output=output_simfile,
        output_type=output_simfile_type,
        invalid_property_behaviors=invalid_property_behaviors,
    )

    for _chart in simfile.charts:
        chart: Chart = _chart  # typing workaround
        output_chart = deepcopy(chart_template) or output_chart_type.blank()
        _copy_properties(
            source=chart,
            output=output_chart,
            output_type=output_chart_type,
            invalid_property_behaviors=invalid_property_behaviors,
        )
        output_simfile.charts.append(output_chart)

    return cast(_CONVERT_SIMFILE, output_simfile)


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

    Not all SSC properties are valid for SM simfiles, including some
    gameplay events and timing data. If one of those types of properties
    are found and contain a non-default value,
    :class:`InvalidPropertyException` will be raised.

    The behavior described above can be changed by supplying the
    `invalid_property_behaviors` parameter, which maps
    :class:`PropertyType` to :class:`InvalidPropertyBehavior` values.
    This mapping need not cover every :class:`PropertyType`; any missing
    values will fall back to the default mapping described
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
