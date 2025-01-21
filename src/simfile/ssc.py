"""
Simfile & chart classes for SSC files.
"""

from collections import Counter
from dataclasses import replace
from typing import Iterable, Optional, Sequence, TextIO, Tuple, Type

from msdparser import parse_msd, MSDParameter
from msdparser.lexer import MSDToken

from simfile._private.ordered_dict_forwarder import Property
from .sm import SM_CHART_PROPERTIES, SM_SIMFILE_PROPERTIES

from .base import (
    BaseAttachedChart,
    BaseChart,
    BaseCharts,
    BaseObject,
    BaseSimfile,
    MSDIterator,
)
from ._private.dedent import dedent_and_trim


__all__ = ["SSCChart", "AttachedSSCChart", "SSCCharts", "SSCSimfile"]


SSC_CHART_PROPERTIES = (
    "NOTEDATA",
    "CHARTNAME",
    "STEPSTYPE",
    "DESCRIPTION",
    "CHARTSTYLE",
    "DIFFICULTY",
    "METER",
    "MUSIC",
    "RADARVALUES",
    "CREDIT",
    "OFFSET",
    "BPMS",
    "STOPS",
    "DELAYS",
    "TIMESIGNATURES",
    "TICKCOUNTS",
    "COMBOS",
    "WARPS",
    "SPEEDS",
    "SCROLLS",
    "FAKES",
    "LABELS",
    "ATTACKS",
    "DISPLAYBPM",
    "NOTES",
    "NOTES2",
)
"""
All chart-level properties of .SSC files recognized by StepMania 5.

This sequence is sorted in the same order produced by the StepMania 5 editor.
"""


class SSCChart(BaseChart):
    """
    SSC implementation of :class:`~simfile.base.BaseChart`.

    Unlike :class:`~simfile.sm.SMChart`, SSC chart metadata is stored
    as key-value pairs, so this class allows full modification of its
    backing OrderedDict.

    Adds the following known properties:

    * Metadata:  `chartname`, `chartstyle`, `credit`, `timesignatures`
    * File paths: `music`
    * Gameplay events: `tickcounts`, `combos`, `speeds`, `scrolls`,
      `fakes`, `attacks`
    * Timing data: `bpms`, `stops`, `delays`, `warps`,
      `labels`, `offset`, `displaybpm`
    """

    chartname = BaseObject._item_property("CHARTNAME")
    chartstyle = BaseObject._item_property("CHARTSTYLE")
    music = BaseObject._item_property("MUSIC")
    credit = BaseObject._item_property("CREDIT")
    offset = BaseObject._item_property("OFFSET")
    bpms = BaseObject._item_property("BPMS")
    stops = BaseObject._item_property("STOPS")
    delays = BaseObject._item_property("DELAYS")
    timesignatures = BaseObject._item_property("TIMESIGNATURES")
    tickcounts = BaseObject._item_property("TICKCOUNTS")
    combos = BaseObject._item_property("COMBOS")
    warps = BaseObject._item_property("WARPS")
    speeds = BaseObject._item_property("SPEEDS")
    scrolls = BaseObject._item_property("SCROLLS")
    fakes = BaseObject._item_property("FAKES")
    labels = BaseObject._item_property("LABELS")
    attacks = BaseObject._item_property("ATTACKS")
    displaybpm = BaseObject._item_property("DISPLAYBPM")

    # "NOTES2" alias only supported by SSC files
    notes = BaseObject._item_property("NOTES", alias="NOTES2")

    @classmethod
    def from_str(cls: Type["SSCChart"], string: str, strict: bool = True) -> "SSCChart":
        """
        Parse a string containing MSD data into an SSC chart.

        The first property's key must be `NOTEDATA`. Parsing ends at
        the `NOTES` (or `NOTES2`) property.

        By default, the underlying parser will throw an exception if it
        finds any stray text between parameters. This behavior can be
        overridden by setting `strict` to False.
        """
        chart = SSCChart()
        chart._parse(parse_msd(string=string, strict=strict))
        return chart

    @classmethod
    def blank(cls: Type["SSCChart"]) -> "SSCChart":
        return cls.from_str(
            """
            #NOTEDATA:;
            #CHARTNAME:;
            #STEPSTYPE:dance-single;
            #DESCRIPTION:;
            #CHARTSTYLE:;
            #DIFFICULTY:Beginner;
            #METER:1;
            #RADARVALUES:0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000;
            #CREDIT:;
            #NOTES:
            0000
            0000
            0000
            0000
            ;
        """
        )

    def _parse(self, parser: MSDIterator) -> None:
        iterator = iter(parser)
        first_key = True
        seen_keys: Counter[str] = Counter()

        for param in iterator:
            upper_key = param.key.upper()

            if first_key and upper_key != "NOTEDATA":
                raise ValueError("expected NOTEDATA property first")
            first_key = False

            if upper_key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                value = ":".join(param.components[1:])
            else:
                value = param.value

            self._set_property(
                upper_key,
                Property(value=value, msd_parameter=param),
                seen_keys=seen_keys,
            )

            if param.value is self.notes:
                break

    def serialize(self, file):
        notedata_property = self._properties["NOTEDATA"] or Property(
            "",
            replace(self._default_parameter, components=("NOTEDATA",)),
        )
        notedata_property.msd_parameter.serialize(file, exact=True)

        notes_key = "NOTES"

        for upper_key, property in self._properties.items():
            if upper_key == "NOTEDATA":
                continue

            if property.msd_parameter.key.upper() == upper_key:
                key = property.msd_parameter.key
            else:
                key = upper_key

            # Either NOTES or NOTES2 must be the last chart property
            if property.value is self.notes:
                notes_key = key
                continue

            if upper_key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                components = (key, *property.value.split(":"))
            else:
                components = (key, property.value)

            # Don't try to preserve comments & exact escapes if the value changed
            preserve_ephemera = property.value == property.msd_parameter.value

            param = MSDParameter(
                components,
                preamble=property.msd_parameter.preamble,
                comments=property.msd_parameter.comments if preserve_ephemera else None,
                escape_positions=(
                    property.msd_parameter.escape_positions
                    if preserve_ephemera
                    else None
                ),
                suffix=property.msd_parameter.suffix,
            )
            param.serialize(file, exact=True)

        notes_property = self._properties.get(notes_key.upper())
        if notes_property:
            notes_param = MSDParameter(
                components=(notes_key, notes_property.value),
                preamble=notes_property.msd_parameter.preamble,
                comments=notes_property.msd_parameter.comments,
                suffix=notes_property.msd_parameter.suffix,
            )

            notes_param.serialize(file, exact=True)

    def _attach(self, simfile: "SSCSimfile") -> "AttachedSSCChart":
        attached = AttachedSSCChart(simfile=simfile)
        attached._properties = self._properties.copy()
        return attached


class AttachedSSCChart(SSCChart, BaseAttachedChart[SSCChart, "SSCSimfile"]):
    def detach(self) -> SSCChart:
        detached = SSCChart()
        detached._properties = self._properties.copy()
        return detached


class SSCCharts(BaseCharts[AttachedSSCChart, "SSCChart", "SSCSimfile"]):
    """
    SSC implementation of :class:`~simfile.base.BaseCharts`.

    List elements are :class:`SSCChart` instances.
    """

    def append(self, chart: SSCChart):
        super().append(chart._attach(self._simfile))

    def extend(self, iterable: Iterable[SSCChart]) -> None:
        return super().extend(chart._attach(self._simfile) for chart in iterable)


SSC_SIMFILE_PROPERTIES = (
    "VERSION",
    "TITLE",
    "SUBTITLE",
    "ARTIST",
    "TITLETRANSLIT",
    "SUBTITLETRANSLIT",
    "ARTISTTRANSLIT",
    "GENRE",
    "ORIGIN",
    "CREDIT",
    "BANNER",
    "BACKGROUND",
    "PREVIEWVID",
    "JACKET",
    "CDIMAGE",
    "DISCIMAGE",
    "LYRICSPATH",
    "CDTITLE",
    "MUSIC",
    "PREVIEW",
    "INSTRUMENTTRACK",
    "OFFSET",
    "SAMPLESTART",
    "SAMPLELENGTH",
    "SELECTABLE",
    "DISPLAYBPM",
    "BPMS",
    "STOPS",
    "DELAYS",
    "WARPS",
    "TIMESIGNATURES",
    "TICKCOUNTS",
    "COMBOS",
    "SPEEDS",
    "SCROLLS",
    "FAKES",
    "LABELS",
    "LASTSECONDHINT",
    "BGCHANGES",
    "FGCHANGES",
    "KEYSOUNDS",
    "ATTACKS",
)
"""
All simfile-level properties of .SSC files recognized by StepMania 5.

This sequence is sorted in the same order produced by the StepMania 5 editor.
"""


class SSCSimfile(BaseSimfile):
    """
    SSC implementation of :class:`~simfile.base.BaseSimfile`.

    Adds the following known properties:

    * SSC version: `version`
    * Metadata: `origin`, `labels`, `lastsecondhint`
    * File paths: `previewvid`, `jacket`, `cdimage`, `discimage`,
      `preview`
    * Gameplay events: `combos`, `speeds`, `scrolls`, `fakes`
    * Timing data: `warps`
    """

    _charts: SSCCharts

    version = BaseObject._item_property("VERSION")
    origin = BaseObject._item_property("ORIGIN")
    previewvid = BaseObject._item_property("PREVIEWVID")
    jacket = BaseObject._item_property("JACKET")
    cdimage = BaseObject._item_property("CDIMAGE")
    discimage = BaseObject._item_property("DISCIMAGE")
    preview = BaseObject._item_property("PREVIEW")
    lastsecondhint = BaseObject._item_property("LASTSECONDHINT")
    warps = BaseObject._item_property("WARPS")
    labels = BaseObject._item_property("LABELS")
    combos = BaseObject._item_property("COMBOS")
    speeds = BaseObject._item_property("SPEEDS")
    scrolls = BaseObject._item_property("SCROLLS")
    fakes = BaseObject._item_property("FAKES")

    def __init__(
        self,
        *,
        file: Optional[TextIO] = None,
        string: Optional[str] = None,
        tokens: Optional[Iterable[Tuple[MSDToken, str]]] = None,
        strict: bool = True,
    ):
        self._charts = SSCCharts(simfile=self)
        super().__init__(file=file, string=string, tokens=tokens, strict=strict)

    @classmethod
    def blank(cls: Type["SSCSimfile"]) -> "SSCSimfile":
        return SSCSimfile(
            string=dedent_and_trim(
                """
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
        """
            )
        )

    def _parse(self, parser: MSDIterator):
        self.charts = SSCCharts(simfile=self)
        partial_chart: Optional[SSCChart] = None
        suffix_heuristic = ";\n"
        suffix_heuristic_match = False
        seen_keys: Counter[str] = Counter()

        for param in self._move_suffix_to_next_preamble(parser, ("NOTEDATA",)):
            # Determine a default parameter suffix from the input
            if not suffix_heuristic_match:
                if param.suffix == suffix_heuristic:
                    suffix_heuristic_match = True
                    self._default_parameter = replace(
                        self._default_parameter, suffix=suffix_heuristic
                    )
                else:
                    suffix_heuristic = param.suffix

            upper_key = param.key.upper()

            if upper_key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                value: Optional[str] = ":".join(param.components[1:])
            else:
                value = param.value

            if upper_key == "NOTEDATA":
                if partial_chart is not None:
                    self.charts.append(partial_chart)
                partial_chart = SSCChart()

            obj = partial_chart if partial_chart is not None else self
            obj._set_property(
                upper_key,
                Property(value=value, msd_parameter=param),
                seen_keys=seen_keys,
            )

        if partial_chart is not None:
            self.charts.append(partial_chart)

    @property
    def charts(self) -> SSCCharts:
        return self._charts

    @charts.setter
    def charts(self, charts: Sequence[SSCChart]):
        self._charts = SSCCharts(simfile=self, charts=charts)
