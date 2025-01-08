from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, replace
import enum
from functools import reduce
from operator import __or__ as _or_
from typing import TypeVar, Literal

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


B = TypeVar("B", bound="BaseBehavior")


class BaseBehavior(enum.Enum, meta=ABCMeta):
    """
    An optional behavior. See enum values for details.
    """

    @abstractmethod
    @classmethod
    def default(cls: type[B]) -> B:
        raise NotImplementedError()

    @abstractmethod
    def run(self, sim: Simfile) -> bool:
        raise NotImplementedError()

    @classmethod
    def run_outer(cls: type[B], sim: Simfile, instance: Literal[True] | B):
        if instance is True:
            return cls.default().run(sim)
        else:
            return instance.run(sim)


class BaseFlagBehavior(enum.Flag, BaseBehavior, meta=ABCMeta):

    @classmethod
    def default(cls):
        cls_name = cls.__name__
        if not len(cls):
            raise AttributeError("empty %s does not have an ALL value" % cls_name)
        value = cls(reduce(_or_, cls))
        cls._member_map_["ALL"] = value
        return value


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


class Whitespace(BaseBehavior):
    SM5 = enum.auto()
    """
    Normalize whitespace to match StepMania 5's output:

    * Properties are separated by a newline.
    * Each chart is prefixed by a blank line.
    """

    @classmethod
    def default(cls):
        return cls.SM5

    def run(self) -> bool:
        return False


class LineEndings(BaseBehavior):
    LF = enum.auto()
    """
    Normalize all line endings to '\\n'.
    """

    CRLF = enum.auto()
    """
    Normalize all line endings to '\\r\\n'.
    """

    @classmethod
    def default(cls):
        return cls.LF

    def run(self) -> bool:
        return False


class RemoveComments(BaseFlagBehavior):
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

    def run(self) -> bool:
        return False


class CreateComments(BaseFlagBehavior):
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

    def run(self) -> bool:
        return False


class CreateDefaultProperties(BaseBehavior):
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

    def run(self) -> bool:
        return False


class DestructivelyRemoveProperties(BaseBehavior):
    SM5 = enum.auto()
    """
    Remove all properties that are unknown to the StepMania 5 editor.
    """

    @classmethod
    def default(cls):
        return cls.SM5

    def run(self) -> bool:
        return False


class SortProperties(BaseBehavior):
    SM5 = enum.auto()
    """
    Sort known properties to match the StepMania 5 editor's output.

    Unknown properties, if not removed, are sorted alphabetically after
    known properties.
    """

    @classmethod
    def default(cls):
        return cls.SM5

    def run(self) -> bool:
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
