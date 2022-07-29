"""
Simfile & chart classes for SM files.
"""
from msdparser import MSDParameter
from simfile._private.property import item_property
from typing import Iterator, List, Optional, Sequence, Type

from .base import BaseChart, BaseCharts, BaseSimfile, MSD_ITERATOR
from ._private.dedent import dedent_and_trim


__all__ = ["SMChart", "SMCharts", "SMSimfile"]


SM_CHART_PROPERTIES = (
    "STEPSTYPE",
    "DESCRIPTION",
    "DIFFICULTY",
    "METER",
    "RADARVALUES",
    "NOTES",
)


class SMChart(BaseChart):
    """
    SM implementation of :class:`~simfile.base.BaseChart`.

    Unlike :class:`~simfile.ssc.SSCChart`, SM chart metadata is stored
    as a fixed list of 6 properties, so this class prohibits adding or
    deleting keys from its backing OrderedDict.
    """

    extradata: Optional[List[str]] = None
    """
    If the chart data contains more than 6 components, the extra
    components will be stored in this attribute.
    """

    @classmethod
    def blank(cls: Type["SMChart"]) -> "SMChart":
        return SMChart.from_str(
            dedent_and_trim(
                """
                 dance-single:
                 :
                 Beginner:
                 1:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000
        """
            )
        )

    @classmethod
    def from_str(cls: Type["SMChart"], string: str) -> "SMChart":
        """
        Parse the serialized MSD value components of a NOTES property.

        The string should contain six colon-separated components,
        corresponding to each of the base known properties documented in
        :class:`.BaseChart`. Any additional components will be stored in
        :data:`extradata`.

        Raises :code:`ValueError` if the string contains fewer than six
        components.

        .. deprecated:: 2.1
            This is now a less efficient version of :func:`from_msd`, which
            interoperates better with ``msdparser`` version 2.0.
        """
        instance = cls()
        instance._from_str(string)
        return instance

    @classmethod
    def from_msd(cls: Type["SMChart"], values: Sequence[str]) -> "SMChart":
        """
        Parse the MSD value components of a NOTES property.

        The list should contain six strings, corresponding to each of the
        base known properties documented in :class:`.BaseChart`. Any
        additional components will be stored in :data:`extradata`.

        Raises :code:`ValueError` if the list contains fewer than six
        components.
        """
        instance = cls()
        instance._from_msd(values)
        return instance

    def _from_str(self, string: str) -> None:
        self._from_msd(string.split(":"))

    def _from_msd(self, values: Sequence[str]) -> None:
        if len(values) < len(SM_CHART_PROPERTIES):
            raise ValueError(
                f"expected at least {len(SM_CHART_PROPERTIES)} "
                f"chart components, got {len(values)}"
            )

        for property, value in zip(SM_CHART_PROPERTIES, values):
            self[property] = value.strip()

        if len(values) > len(SM_CHART_PROPERTIES):
            self.extradata = list(values[len(SM_CHART_PROPERTIES) :])

    def _parse(self, parser: Iterator[MSDParameter]):
        param = next(parser)
        if param.key.upper() != "NOTES":
            raise ValueError(f"expected a NOTES property, got {property}")

        self._from_msd(param.components[1:])

    def serialize(self, file):
        param = MSDParameter(
            (
                "NOTES",
                f"\n     {self.stepstype}",
                f"\n     {self.description}",
                f"\n     {self.difficulty}",
                f"\n     {self.meter}",
                f"\n     {self.radarvalues}",
                f"\n{self.notes}\n",
                *(self.extradata or []),
            )
        )
        file.write(str(param))

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.stepstype == other.stepstype
            and self.description == other.description
            and self.difficulty == other.difficulty
            and self.meter == other.meter
            and self.radarvalues == other.radarvalues
            and self.notes == other.notes
        )

    # Prevent keys from being added or removed

    def update(self, *args, **kwargs) -> None:
        """Raises NotImplementedError."""
        # This could be implemented, but I don't see a use case
        raise NotImplementedError

    def pop(self, property, default=None):
        """Raises NotImplementedError."""
        raise NotImplementedError

    def popitem(self, last=True):
        """Raises NotImplementedError."""
        raise NotImplementedError

    def __getitem__(self, property):
        if property in SM_CHART_PROPERTIES:
            return getattr(self, property.lower())
        else:
            raise KeyError

    def __setitem__(self, property: str, value: str) -> None:
        if property.upper() not in SM_CHART_PROPERTIES:
            raise KeyError
        else:
            return super().__setitem__(property, value)

    def __delitem__(self, property: str) -> None:
        """Raises NotImplementedError."""
        raise NotImplementedError


class SMCharts(BaseCharts[SMChart]):
    """
    SM implementation of :class:`~simfile.base.BaseCharts`.

    List elements are :class:`SMChart` instances.
    """


class SMSimfile(BaseSimfile):
    """
    SM implementation of :class:`~simfile.base.BaseSimfile`.
    """

    _charts: SMCharts

    # "FREEZES" alias only supported by SM files
    stops = item_property("STOPS", alias="FREEZES")
    """
    Specialized property for `STOPS` that supports `FREEZES` as an alias.
    """

    def _parse(self, parser: MSD_ITERATOR):
        self._charts = SMCharts()
        for param in parser:
            key = param.key.upper()
            if key == "NOTES":
                self.charts.append(SMChart.from_msd(param.components[1:]))
            elif key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                self[key] = ":".join(param.components[1:])
            else:
                self[key] = param.value

    @classmethod
    def blank(cls: Type["SMSimfile"]) -> "SMSimfile":
        return SMSimfile(
            string=dedent_and_trim(
                """
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
        """
            )
        )

    @property
    def charts(self) -> SMCharts:
        return self._charts

    @charts.setter
    def charts(self, charts: Sequence[SMChart]):
        self._charts = SMCharts(charts)
