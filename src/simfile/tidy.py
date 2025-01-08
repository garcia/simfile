import enum
from typing import Optional

from simfile.types import Simfile


class Preset(enum.Enum):
    NO_OP = enum.auto()
    """
    Leave all optional behaviors off by default.
    
    This is equivalent to not specifying a preset, except it allows you to
    leave all optional behaviors ``False``.
    """

    SM5 = enum.auto()
    """
    Emulate the StepMania 5 editor's output.
    """

    ALL_NONDESTRUCTIVE = enum.auto()
    """
    Equivalent to specifying ``True`` for all _nondestructive_ behaviors.
    """


class Whitespace(enum.Enum):
    SM5 = enum.auto()
    """
    Normalize whitespace to match StepMania 5's output:

    * Properties are separated by a newline.
    * Each chart is prefixed by a blank line.
    """


class LineEndings(enum.Enum):
    LF = enum.auto()
    """
    Normalize all line endings to '\\n'.
    """

    CRLF = enum.auto()
    """
    Normalize all line endings to '\\r\\n'.
    """


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


class DestructivelyRemoveProperties(enum.Enum):
    SM5 = enum.auto()
    """
    Remove all properties that are unknown to the StepMania 5 editor.
    """


class SortProperties(enum.Enum):
    SM5 = enum.auto()
    """
    Sort known properties to match the StepMania 5 editor's output.

    Unknown properties, if not removed, are sorted alphabetically after
    known properties.
    """


def tidy(
    sim: Simfile,
    preset: Optional[Preset] = None,
    *,
    whitespace: bool = False,
    line_endings: bool | LineEndings = False,
    remove_comments: bool | RemoveComments = False,
    create_comments: bool | CreateComments = False,
    create_default_properties: bool | CreateDefaultProperties = False,
    destructively_remove_properties: bool | DestructivelyRemoveProperties = False,
    sort_properties: bool | SortProperties = False,
):
    """
    Tidy up a simfile for serialization to disk.

    This function has many optional parameters that toggle various
    tidying behaviors. The simplest way to call it is to pass a preset
    as the second argument::

        import tidy, Preset from simfile.tidy
        tidy(sim, Preset.SM5)

    Without a preset, all options default to False. You must specify at
    least one optional behavior, or specify the :data:`~.NO_OP` preset
    to allow no behaviors.

    Each optional behavior has an associated enum. Some enums are flags
    that can be combined using bitwise operators, like so::

        tidy(
            sim,
            filter_comments=FilterComments.PREAMBLE | FilterComments.CHART_PREAMBLE,
        )

    Optional behaviors also take the shorthand `True` to opt into a default
    behavior. For non-flag enums, this is equivalent to passing the first
    enum value. For flag enums, it's equivalent to combining all options.
    """
    raise NotImplementedError()
