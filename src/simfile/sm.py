"""
Simfile & chart classes for SM files.
"""

from msdparser import MSDParameter
from typing import Iterator, List, Optional, Sequence, Type

from simfile._private.ordered_dict_forwarder import Property

from .base import BaseChart, BaseCharts, BaseObject, BaseSimfile, MSDIterator
from ._private.dedent import dedent_and_trim


__all__ = ["SMChart", "AttachedSMChart", "SMCharts", "SMSimfile"]


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
        return SMChart.from_msd(string.split(":"))

    @classmethod
    def from_msd(cls: Type["SMChart"], values: Sequence[str]) -> "SMChart":
        """
        Parse the MSD value components of a NOTES property.

        The list should contain six strings, corresponding to each of the
        base known properties documented in :class:`.BaseChart`. Any
        additional components will be stored in :data:`extradata`.

        Raises :code:`ValueError` if the list contains fewer than six
        components.

        .. deprecated:: 3.0
            Use :func:`from_msd_parameter` instead. This method doesn't
            preserve whitespace or comments.
        """
        return SMChart.from_msd_parameter(
            MSDParameter(components=["NOTES"] + list(values), suffix=";\n\n")
        )

    @classmethod
    def from_msd_parameter(cls: Type["SMChart"], param: MSDParameter) -> "SMChart":
        """
        Parse a NOTES parameter from an SM file.

        The parameter should contain seven components, corresponding to
        the "NOTES" key followed by the six base known properties
        documented in :class:`.BaseChart`. Any additional components
        will be stored in :data:`extradata`.

        Raises :code:`ValueError` if the parameter contains <7 components.
        """
        instance = cls()
        instance._from_msd(param)
        return instance

    def _from_msd(self, param: MSDParameter) -> None:
        # Subtract 1 for the key component
        if len(param.components) - 1 < len(SM_CHART_PROPERTIES):
            raise ValueError(
                f"expected at least {len(SM_CHART_PROPERTIES)} "
                f"chart components, got {len(param.components)}"
            )

        # SMChart abuses the _properties OrderedDict to preserve whitespace
        # for things that are technically not MSD parameters themselves.
        # Here we store the input param under a NOTES pseudo-param.
        self._properties["OUTER"] = Property(
            "",  # unused
            msd_parameter=MSDParameter(
                # TODO: cache all the components, not just the key
                # (we need this so we can determine if the comments should be removed)
                components=(param.key,),
                comments=param.comments,
                preamble=param.preamble,
                suffix=param.suffix,
            ),
        )

        for property, value in zip(SM_CHART_PROPERTIES, param.components[1:]):
            leading_ws = value[: len(value) - len(value.lstrip())]
            trailing_ws = value[len(value.rstrip()) :]
            # Here we store the whitespace around each component
            # as pseudo-properties with a preamble & suffix.
            self._properties[property] = Property(
                value=value.strip(),
                msd_parameter=MSDParameter(
                    components=(value,),
                    preamble=leading_ws,
                    suffix=trailing_ws,
                ),
            )

        if len(param.components) - 1 > len(SM_CHART_PROPERTIES):
            self.extradata = list(param.components[len(SM_CHART_PROPERTIES) + 1 :])

    def _parse(self, parser: Iterator[MSDParameter]):
        param = next(parser)
        if param.key.upper() != "NOTES":
            raise ValueError(f"expected a NOTES property, got {property}")

        self._from_msd(param)

    def serialize(self, file):
        def serialize_field(property: Property):
            return (
                (property.msd_parameter.preamble or "")  # whitespace before field
                + property.value
                + property.msd_parameter.suffix  # whitespace after field
            )

        # Pseudo-param for the whole NOTES parameter
        # (Includes comments & actual ';' suffix)
        notes_param = self._properties["OUTER"].msd_parameter

        param = MSDParameter(
            components=(
                "NOTES",
                *(
                    serialize_field(self._properties[field])
                    for field in SM_CHART_PROPERTIES
                ),
                *(self.extradata or ()),
            ),
            preamble=notes_param.preamble,
            comments=notes_param.comments,
            suffix=notes_param.suffix,
        )
        file.write(param.stringify(exact=True))

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
            BaseObject.__setitem__(self, property, value)

    def __delitem__(self, property: str) -> None:
        """Raises NotImplementedError."""
        raise NotImplementedError

    # Prevent the pseudo "OUTER" item from leaking
    def items(self) -> Sequence[tuple[str, str]]:
        return [
            (key, property.value)
            for key, property in self._properties.items()
            if key != "OUTER"
        ]


class AttachedSMChart(SMChart):
    _simfile: "SMSimfile"

    def __init__(self, simfile: "SMSimfile"):
        super().__init__()
        self._simfile = simfile

    def detach(self) -> SMChart:
        detached = SMChart()
        detached._properties = self._properties.copy()
        return detached


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
    stops = BaseObject._item_property("STOPS", alias="FREEZES")
    """
    Specialized property for `STOPS` that supports `FREEZES` as an alias.
    """

    def _parse(self, parser: MSDIterator):
        self._charts = SMCharts()
        for param in parser:
            upper_key = param.key.upper()
            if upper_key == "NOTES":
                self.charts.append(SMChart.from_msd_parameter(param))
            elif upper_key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                self._properties[upper_key] = Property(
                    value=":".join(param.components[1:]),
                    msd_parameter=param,
                )
            else:
                self._properties[upper_key] = Property(
                    value=param.value, msd_parameter=param
                )

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
