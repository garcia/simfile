from dataclasses import dataclass, replace
import enum
from typing import Optional
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

    @classmethod
    def default(cls):
        return cls.NO_OP

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
    """

    @classmethod
    def default(cls):
        return cls.SM5

    def run(self, sim: Simfile) -> bool:
        if self is Whitespace.SM5:
            nl = "\r\n" if "\r\n" in sim._default_parameter.suffix else "\n"

            def sm5_chart_preamble(existing_preamble: Optional[str]):
                if not existing_preamble or existing_preamble.isspace():
                    return nl
                else:
                    return f"{nl}{existing_preamble.strip()}{nl}"

            sim._default_parameter = replace(sim._default_parameter, suffix=f";{nl}")
            for property in sim._properties.values():
                property.msd_parameter = replace(
                    property.msd_parameter, suffix=sim._default_parameter.suffix
                )

            for chart in sim.charts:

                if isinstance(chart, SMChart):
                    # Normalize whitespace before the (real) chart property
                    chart._real_parameter = replace(
                        chart._real_parameter,
                        preamble=sm5_chart_preamble(chart._real_parameter.preamble),
                        suffix=sim._default_parameter.suffix,
                    )

                    # Normalize whitespace between each (pseudo) property
                    for key, property in chart._properties.items():
                        if key == "NOTES":
                            property.msd_parameter = replace(
                                property.msd_parameter, preamble=nl, suffix=nl
                            )
                        else:
                            property.msd_parameter = replace(
                                property.msd_parameter, preamble=f"{nl}     "
                            )

                elif isinstance(chart, SSCChart):
                    # Normalize whitespace before the chart
                    notedata = chart._properties["NOTEDATA"]
                    notedata.msd_parameter = replace(
                        notedata.msd_parameter,
                        preamble=sm5_chart_preamble(notedata.msd_parameter.preamble),
                    )

                    # Normalize whitespace between each property
                    for property in chart._properties.values():
                        property.msd_parameter = replace(
                            property.msd_parameter, suffix=sim._default_parameter.suffix
                        )
                else:
                    assert_never(chart)

            return True

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

    @classmethod
    def default(cls):
        return cls.LF

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

    @classmethod
    def default(cls):
        return cls.SM5_DEFAULT

    def run(self, sim: Simfile) -> bool:
        return False


class DestructivelyRemoveProperties(enum.Enum):
    SM5 = enum.auto()
    """
    Remove all properties that are unknown to the StepMania 5 editor.
    """

    @classmethod
    def default(cls):
        return cls.SM5

    def run(self, sim: Simfile) -> bool:
        return False


class SortProperties(enum.Enum):
    SM5 = enum.auto()
    """
    Sort known properties to match the StepMania 5 editor's output.

    Unknown properties, if not removed, are sorted alphabetically after
    known properties.
    """

    @classmethod
    def default(cls):
        return cls.SM5

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
