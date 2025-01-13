from dataclasses import dataclass, replace
import enum
from typing import Optional
from msdparser import MSDParameter
from typing_extensions import assert_never

from simfile.sm import SMChart
from simfile.ssc import SSCChart
from simfile.types import Simfile


__all__ = [
    "Preset",
    "Whitespace",
    "LineEndings",
    "RemoveComments",
    "CreateComments",
    "CreateDefaultProperties",
    "DestructivelyRemoveProperties",
    "SortProperties",
]


class Preset(enum.Enum):
    """
    A predefined set of behaviors for use with :func:`~.tidy`.
    """

    NO_OP = enum.auto()
    """
    Leave all optional behaviors off by default.
    
    This is equivalent to not specifying a preset, except it allows you to
    leave all optional behaviors ``False``.
    """

    SM5 = enum.auto()
    """
    Emulate the StepMania 5 editor's output (nondestructively).
    """

    SM5_DESTRUCTIVE = enum.auto()
    """
    Emulate the StepMania 5 editor's output (including removing unknown
    properties).
    """

    ALL_NONDESTRUCTIVE = enum.auto()
    """
    Equivalent to specifying ``True`` for all _nondestructive_ behaviors.
    """

    def behaviors(self) -> "DefaultBehaviors":
        if self is Preset.NO_OP:
            return DefaultBehaviors()
        elif self is Preset.SM5:
            return replace(
                DefaultBehaviors(),
                whitespace=Whitespace.SM5,
                line_endings=LineEndings.LF,
                remove_comments=RemoveComments.PREAMBLE | RemoveComments.OTHER,
                create_comments=CreateComments.CHART_PREAMBLE
                | CreateComments.CHART_MEASURES,
                create_default_properties=CreateDefaultProperties.SM5_DEFAULT,
                destructively_remove_properties=False,
                sort_properties=SortProperties.SM5,
            )
        elif self is Preset.SM5_DESTRUCTIVE:
            return replace(
                Preset.SM5.behaviors(),
                destructively_remove_properties=DestructivelyRemoveProperties.SM5,
            )
        else:
            assert False


class Whitespace(enum.Enum):
    SM5 = enum.auto()
    """
    Normalize whitespace to match StepMania 5's output:

    * Properties are separated by a newline.
    * Each chart is prefixed by a blank line.
    * Each SM chart property (before note data) is prefixed by 5 spaces.

    Currently, this option removes comments inside of SM charts
    if their whitespace is adjusted. Combine with :class:`.CreateComments`
    to regenerate measure comments if desired.
    """

    def run(self, sim: Simfile) -> bool:
        changed = False

        if self is Whitespace.SM5:
            # Extract newline from heursitic-determined suffix
            nl = "\r\n" if "\r\n" in sim._default_parameter.suffix else "\n"

            # Normalize suffix & (optionally) preamble whitespace
            def normalize_ws(param: MSDParameter, preamble=False) -> MSDParameter:
                if preamble:
                    # Blank / empty -> single newline
                    if not param.preamble or param.preamble.isspace():
                        new_preamble = nl
                    # Non-empty -> strip & pad with newline on each side
                    else:
                        new_preamble = f"{nl}{param.preamble.strip()}{nl}"
                else:
                    new_preamble = param.preamble

                suffix_no_semicolon = param.suffix.removeprefix(";")
                # Blank / empty -> semicolon followed by newline
                if suffix_no_semicolon == "" or suffix_no_semicolon.isspace():
                    new_suffix = f";{nl}"
                # Non-empty -> ensure semicolon & one trailing newline
                else:
                    new_suffix = f";{suffix_no_semicolon.rstrip()}{nl}"

                return replace(param, preamble=new_preamble, suffix=new_suffix)

            if sim._default_parameter.suffix != f";{nl}":
                sim._default_parameter = replace(
                    sim._default_parameter, suffix=f";{nl}"
                )
                changed = True

            for property in sim._properties.values():
                normalized_ws = normalize_ws(property.msd_parameter)
                if property.msd_parameter != normalized_ws:
                    property.msd_parameter = normalized_ws
                    changed = True

            for chart in sim.charts:

                # This is tricky to get right on SMChart
                # because of the way it abuses the _properties dict.
                if isinstance(chart, SMChart):
                    # Normalize whitespace before the (real) chart property
                    normalized_ws = normalize_ws(chart._real_parameter, preamble=True)
                    if chart._real_parameter != normalized_ws:
                        chart._real_parameter = normalized_ws
                        changed = True

                    # Normalize whitespace between each (pseudo) property
                    # TODO: check how this interacts with escape & comment MSD data
                    for key, property in chart._properties.items():
                        sm_chart_changed = False
                        if key == "NOTES":
                            updated_parameter = replace(
                                property.msd_parameter, suffix=nl
                            )
                            if property.msd_parameter != updated_parameter:
                                property.msd_parameter = updated_parameter
                                sm_chart_changed = True
                        else:
                            updated_parameter = replace(
                                property.msd_parameter, preamble=f"{nl}     "
                            )
                            if property.msd_parameter != updated_parameter:
                                property.msd_parameter = updated_parameter
                                sm_chart_changed = True

                        # Adjusting whitespace *inside* of an MSD parameter
                        # invalidates the escape & comment positions;
                        # we could try to keep track of the positions,
                        # but for now, just reset it and let msdparser
                        # regenerate any necessary escapes.
                        if sm_chart_changed:
                            chart._real_parameter = replace(
                                chart._real_parameter,
                                escape_positions=None,
                                comments=None,
                            )

                        changed |= sm_chart_changed

                elif isinstance(chart, SSCChart):
                    # Normalize whitespace before the chart
                    notedata = chart._properties["NOTEDATA"]
                    normalized_ws = normalize_ws(notedata.msd_parameter, preamble=True)
                    if notedata.msd_parameter != normalized_ws:
                        notedata.msd_parameter = normalized_ws
                        changed = True

                    # Normalize whitespace between each property
                    for property in chart._properties.values():
                        normalized_ws = normalize_ws(property.msd_parameter)
                        if property.msd_parameter != normalized_ws:
                            property.msd_parameter = normalized_ws
                            changed = True
                else:
                    assert_never(chart)

            return changed

        else:
            assert_never(self)


class LineEndings(enum.Enum):
    LF = enum.auto()
    """
    Normalize all line endings to '\\n'.
    """

    CRLF = enum.auto()
    """
    Normalize all line endings to '\\r\\n'.
    """

    HEURISTIC = enum.auto()
    """
    Use the heuristic-determined line ending.

    This typically matches the first line ending seen in the file.
    """

    def run(self, sim: Simfile) -> bool:
        return False


class RemoveComments(enum.Flag):
    PREAMBLE = enum.auto()
    """
    Remove any preamble (comment at the start of the file).
    """

    CHART_PREAMBLE = enum.auto()
    """
    Remove any chart preamble (comment before the first property signaling
    a chart, i.e. ``NOTES`` for SM and ``NOTEDATA`` for SSC).
    """

    CHART_INNER = enum.auto()
    """
    Remove any comments inside a chart, such as (but not limited to)
    measure indicators.
    """

    OTHER = enum.auto()
    """
    Remove any other comments that don't match the above definitions.
    """

    def run(self, sim: Simfile) -> bool:
        return False


class CreateComments(enum.Flag):
    LIBRARY_VERSION_PREAMBLE = enum.auto()
    """
    Create a comment at the start of the file with the following string::

        // Generated using simfile {VERSION} for Python
    
    :code:`{VERSION}` is replaced with :data:`simfile.__version__`.
    """

    CHART_PREAMBLE = enum.auto()
    """
    Create a comment before each chart with the following string::

        //---------------{STEPSTYPE} - {CREDIT}----------------
    
    :code:`{STEPSTYPE}` is replaced by :attr:`Simfile.stepstype` and
    :code:`{CREDIT}` is replaced by :attr:`SMSimfile.description` or
    :attr:`SSCSimfile.credit` as applicable.
    """

    CHART_MEASURES = enum.auto()
    """
    Create comments before each measure to indicate the measure number::

        #NOTES:
        // measure 0
        0000
        0000
        0000
        0000
        ,  // measure 1
        (etc.)
    """

    def run(self, sim: Simfile) -> bool:
        return False


class CreateDefaultProperties(enum.Enum):
    SM5_DEFAULT = enum.auto()
    """
    Create the same default properties that the StepMania 5 editor creates,
    if they don't already exist.

    Most properties' default values are an empty string, but some have a
    specific non-empty default value, such as ``OFFSET`` and ``BPMS``.
    """

    SM5_ALL = enum.auto()
    """
    Like :data:`.SM5_DEFAULT`, but also creates some default properties
    that the StepMania 5 editor leaves out when blank, such as
    ``DISPLAYBPM``.
    """

    def run(self, sim: Simfile) -> bool:
        return False


class DestructivelyRemoveProperties(enum.Enum):
    SM5 = enum.auto()
    """
    Remove all properties that are unknown to the StepMania 5 editor.
    """

    def run(self, sim: Simfile) -> bool:
        return False


class SortProperties(enum.Enum):
    SM5 = enum.auto()
    """
    Sort known properties to match the StepMania 5 editor's output.

    Unknown properties, if not removed, are sorted alphabetically after
    known properties.
    """

    def run(self, sim: Simfile) -> bool:
        return False


@dataclass
class DefaultBehaviors:
    preset: bool | Preset = False
    whitespace: bool | Whitespace = False
    line_endings: bool | LineEndings = False
    remove_comments: bool | RemoveComments = False
    create_comments: bool | CreateComments = False
    create_default_properties: bool | CreateDefaultProperties = False
    destructively_remove_properties: bool | DestructivelyRemoveProperties = False
    sort_properties: bool | SortProperties = False
