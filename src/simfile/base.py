"""
Base classes for simfile & chart implementations.

This module should ideally never need to be used directly, but its
documentation may be useful for understanding the similarities between
the SM and SSC formats.
"""

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from io import StringIO
from typing import Iterable, Iterator, Optional, TextIO, Tuple, Type, TypeVar, Union

from msdparser import parse_msd, MSDParameter
from msdparser.lexer import MSDToken

from ._private.generic import ListWithRepr
from ._private.ordered_dict_forwarder import (
    OrderedDictForwarder,
    OrderedDictPropertyForwarder,
    Property,
)
from ._private.msd_serializable import MSDSerializable


__all__ = ["BaseChart", "BaseCharts", "BaseSimfile"]


MSDIterator = Iterator[MSDParameter]


class BaseObject(MSDSerializable, OrderedDictPropertyForwarder, metaclass=ABCMeta):
    @staticmethod
    def _item_property(name: str, alias: Optional[str] = None):

        # Decide whether to use the property's alias instead of its primary name
        def _name_or_alias(self):
            if name not in self and alias and alias in self:
                return alias
            else:
                return name.upper()

        @property
        def item_property(self: OrderedDictPropertyForwarder) -> Optional[str]:
            property = self._properties.get(_name_or_alias(self))
            return property.value if property else None

        @item_property.setter
        def item_property(self: OrderedDictPropertyForwarder, value: str) -> None:
            key = _name_or_alias(self)
            if not key in self._properties:
                default_msd_parameter = self._default_property.msd_parameter
                self._properties[key] = Property(
                    value=value,
                    msd_parameter=MSDParameter(
                        components=(key, value),
                        comments=default_msd_parameter.comments,
                        preamble=default_msd_parameter.preamble,
                        suffix=default_msd_parameter.suffix,
                    ),
                )
            self._properties[key].value = value

        @item_property.deleter
        def item_property(self: OrderedDictPropertyForwarder) -> None:
            del self._properties[_name_or_alias(self)]

        return item_property

    def __eq__(self, other):
        """
        Test for equality with another BaseChart.

        Two charts are equal if they have the same type and properties.
        """
        return type(self) is type(other) and all(
            a[0] == b[0] and a[1].value == b[1].value
            for a, b in zip(self._properties.items(), other._properties.items())
        )


class BaseChart(BaseObject, metaclass=ABCMeta):
    """
    One chart from a simfile.

    All charts have the following known properties: `stepstype`,
    `description`, `difficulty`, `meter`, `radarvalues`, and `notes`.
    """

    _properties: "OrderedDict[str, Property]"
    _default_property: Property

    stepstype = BaseObject._item_property("STEPSTYPE")
    description = BaseObject._item_property("DESCRIPTION")
    difficulty = BaseObject._item_property("DIFFICULTY")
    meter = BaseObject._item_property("METER")
    radarvalues = BaseObject._item_property("RADARVALUES")
    notes = BaseObject._item_property("NOTES")

    def __init__(self):
        self._properties = OrderedDict()
        self._default_property = Property("", MSDParameter(("",), suffix=";\n"))

    @abstractmethod
    def _parse(self, parser: MSDIterator):
        pass

    @classmethod
    @abstractmethod
    def blank(cls):
        """
        Generate a blank, valid chart populated with standard keys.

        This should approximately match blank charts produced by the
        StepMania editor.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Pretty repr() for charts.

        Includes the class name, stepstype, difficulty, and meter.
        """
        cls = self.__class__.__name__
        return f"<{cls}: {self.stepstype} {self.difficulty} {self.meter}>"


C = TypeVar("C", bound=BaseChart)


class BaseCharts(ListWithRepr[C], MSDSerializable, metaclass=ABCMeta):
    """
    List containing all of a simfile's charts.
    """

    def __init__(self, data=None):
        super().__init__(data)

    def serialize(self, file: TextIO):
        for chart in self:
            chart.serialize(file)


class BaseSimfile(BaseObject, metaclass=ABCMeta):
    """
    A simfile, including its metadata (e.g. song title) and charts.

    Metadata is stored directly on the simfile object through a
    dict-like interface. Keys are unique (if there are duplicates, the
    last value wins) and converted to uppercase.

    Additionally, properties recognized by the current stable version
    of StepMania are exposed through lower-case properties on the
    object for easy (and implicitly spell-checked) access. The
    following known properties are defined:

    * Metadata: `title`, `subtitle`, `artist`, `titletranslit`,
      `subtitletranslit`, `artisttranslit`, `genre`, `credit`,
      `samplestart`, `samplelength`, `selectable`, `instrumenttrack`,
      `timesignatures`
    * File paths: `banner`, `background`, `lyricspath`, `cdtitle`,
      `music`
    * Gameplay events: `bgchanges`, `fgchanges`, `keysounds`, `attacks`,
      `tickcounts`
    * Timing data: `offset`, `bpms`, `stops`, `delays`

    If a desired simfile property isn't in this list, it can still be
    accessed as a dict item.

    By default, the underlying parser will throw an exception if it
    finds any stray text between parameters. This behavior can be
    overridden by setting `strict` to False in the constructor.
    """

    _properties: "OrderedDict[str, Property]"
    _default_property: Property
    _strict: bool

    MULTI_VALUE_PROPERTIES = ("ATTACKS", "DISPLAYBPM")

    title = BaseObject._item_property("TITLE")
    subtitle = BaseObject._item_property("SUBTITLE")
    artist = BaseObject._item_property("ARTIST")
    titletranslit = BaseObject._item_property("TITLETRANSLIT")
    subtitletranslit = BaseObject._item_property("SUBTITLETRANSLIT")
    artisttranslit = BaseObject._item_property("ARTISTTRANSLIT")
    genre = BaseObject._item_property("GENRE")
    credit = BaseObject._item_property("CREDIT")
    banner = BaseObject._item_property("BANNER")
    background = BaseObject._item_property("BACKGROUND")
    lyricspath = BaseObject._item_property("LYRICSPATH")
    cdtitle = BaseObject._item_property("CDTITLE")
    music = BaseObject._item_property("MUSIC")
    offset = BaseObject._item_property("OFFSET")
    bpms = BaseObject._item_property("BPMS")
    stops = BaseObject._item_property("STOPS")
    delays = BaseObject._item_property("DELAYS")
    timesignatures = BaseObject._item_property("TIMESIGNATURES")
    tickcounts = BaseObject._item_property("TICKCOUNTS")
    instrumenttrack = BaseObject._item_property("INSTRUMENTTRACK")
    samplestart = BaseObject._item_property("SAMPLESTART")
    samplelength = BaseObject._item_property("SAMPLELENGTH")
    displaybpm = BaseObject._item_property("DISPLAYBPM")
    selectable = BaseObject._item_property("SELECTABLE")
    bgchanges = BaseObject._item_property("BGCHANGES", alias="ANIMATIONS")
    fgchanges = BaseObject._item_property("FGCHANGES")
    keysounds = BaseObject._item_property("KEYSOUNDS")
    attacks = BaseObject._item_property("ATTACKS")

    @property
    @abstractmethod
    def charts(self) -> BaseCharts:
        """
        List of charts associated with this simfile.
        """

    def __init__(
        self,
        *,
        file: Optional[TextIO] = None,
        string: Optional[str] = None,
        tokens: Optional[Iterable[Tuple[MSDToken, str]]] = None,
        strict: bool = True,
    ):
        self._properties = OrderedDict()
        self._default_property = Property("", MSDParameter(("",), suffix=";\n"))
        self._strict = strict

        provided_inputs = [inp for inp in [file, string, tokens] if inp is not None]
        if len(provided_inputs) > 1:
            raise TypeError(
                "Only one of `file`, `string`, or `tokens` should be supplied"
            )

        if file is not None or string is not None or tokens is not None:
            self._parse(
                parse_msd(
                    file=file,
                    string=string,
                    tokens=tokens,
                    strict=strict,
                )
            )

    @abstractmethod
    def _parse(self, parser: MSDIterator):
        pass

    @classmethod
    @abstractmethod
    def blank(cls):
        """
        Generate a blank, valid simfile populated with standard keys.

        This should approximately match the simfile produced by the
        StepMania editor in a directory with no .sm or .ssc files.
        """

    def serialize(self, file: TextIO):
        for key, value in self._properties.items():
            if key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                components = (key, *value.value.split(":"))
            else:
                components = (key, value.value)
            param = MSDParameter(
                components,
                preamble=value.msd_parameter.preamble,
                comments=value.msd_parameter.comments,
                suffix=value.msd_parameter.suffix,
            )
            param.serialize(file, exact=True)

        self.charts.serialize(file)

    def __repr__(self) -> str:
        """
        Pretty repr() for simfiles.

        Includes the class name, title, and subtitle.
        """
        rtn = "<" + self.__class__.__name__
        if self.title:
            rtn += ": " + self.title
            if self.subtitle:
                rtn += " " + self.subtitle
        return rtn + ">"

    def __eq__(self, other):
        """
        Test for equality with another BaseSimfile.

        Two simfiles are equal if they have the same type, parameters, and
        charts.
        """
        return BaseObject.__eq__(self, other) and self.charts == other.charts

    def __ne__(self, other):
        """
        Test for inequality with another BaseSimfile.
        """
        return not self.__eq__(other)
