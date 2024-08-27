"""
Simfile & chart classes for SSC files.
"""

from typing import Optional, Sequence, Type

from msdparser import parse_msd, MSDParameter

from .base import BaseChart, BaseCharts, BaseSimfile, MSDIterator, _item_property
from ._private.dedent import dedent_and_trim


__all__ = ["SSCChart", "AttachedSSCChart", "SSCCharts", "SSCSimfile"]


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

    chartname = _item_property("CHARTNAME")
    chartstyle = _item_property("CHARTSTYLE")
    credit = _item_property("CREDIT")
    music = _item_property("MUSIC")
    bpms = _item_property("BPMS")
    stops = _item_property("STOPS")
    delays = _item_property("DELAYS")
    timesignatures = _item_property("TIMESIGNATURES")
    tickcounts = _item_property("TICKCOUNTS")
    combos = _item_property("COMBOS")
    warps = _item_property("WARPS")
    speeds = _item_property("SPEEDS")
    scrolls = _item_property("SCROLLS")
    fakes = _item_property("FAKES")
    labels = _item_property("LABELS")
    attacks = _item_property("ATTACKS")
    offset = _item_property("OFFSET")
    displaybpm = _item_property("DISPLAYBPM")

    # "NOTES2" alias only supported by SSC files
    notes = _item_property("NOTES", alias="NOTES2")

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
        chart._parse(parse_msd(string=string, ignore_stray_text=not strict))
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

        param = next(iterator)
        if param.key.upper() != "NOTEDATA":
            raise ValueError("expected NOTEDATA property first")

        for param in iterator:
            if param.key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                self._properties[param.key] = ":".join(param.components[1:])
            else:
                self._properties[param.key] = param.value or ""
            if param.value is self.notes:
                break

    def serialize(self, file):
        file.write(f"{MSDParameter(('NOTEDATA', ''))}\n")
        notes_key = "NOTES"

        for key, value in self._properties.items():
            # Either NOTES or NOTES2 must be the last chart property
            if value is self.notes:
                notes_key = key
                continue
            if key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                param = MSDParameter((key, *value.split(":")))
            else:
                param = MSDParameter((key, value))
            file.write(f"{param}\n")

        notes_param = MSDParameter((notes_key, self._properties[notes_key]))
        file.write(f"{notes_param}\n\n")

    def _attach(self, simfile: "SSCSimfile") -> "AttachedSSCChart":
        attached = AttachedSSCChart(simfile=simfile)
        attached._properties = self._properties.copy()
        return attached


class AttachedSSCChart(SSCChart):
    _simfile: "SSCSimfile"

    def __init__(self, simfile: "SSCSimfile"):
        super().__init__()
        self._simfile = simfile

    def detach(self) -> SSCChart:
        detached = SSCChart()
        detached._properties = self._properties.copy()
        return detached


class SSCCharts(BaseCharts[SSCChart]):
    """
    SSC implementation of :class:`~simfile.base.BaseCharts`.

    List elements are :class:`SSCChart` instances.
    """


class SSCSimfile(BaseSimfile):
    """
    SSC implementation of :class:`~simfile.base.BaseSimfile`.

    Adds the following known properties:

    * SSC version: `version`
    * Metadata: `origin`, `labels`, `musiclength`, `lastsecondhint`
    * File paths: `previewvid`, `jacket`, `cdimage`, `discimage`,
      `preview`
    * Gameplay events: `combos`, `speeds`, `scrolls`, `fakes`
    * Timing data: `warps`
    """

    _charts: SSCCharts

    version = _item_property("VERSION")
    origin = _item_property("ORIGIN")
    previewvid = _item_property("PREVIEWVID")
    jacket = _item_property("JACKET")
    cdimage = _item_property("CDIMAGE")
    discimage = _item_property("DISCIMAGE")
    preview = _item_property("PREVIEW")
    musiclength = _item_property("MUSICLENGTH")
    lastsecondhint = _item_property("LASTSECONDHINT")
    warps = _item_property("WARPS")
    labels = _item_property("LABELS")
    combos = _item_property("COMBOS")
    speeds = _item_property("SPEEDS")
    scrolls = _item_property("SCROLLS")
    fakes = _item_property("FAKES")

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
        self.charts = SSCCharts()
        partial_chart: Optional[SSCChart] = None
        for param in parser:
            key = param.key.upper()
            if key in BaseSimfile.MULTI_VALUE_PROPERTIES:
                value: Optional[str] = ":".join(param.components[1:])
            else:
                value = param.value
            if key == "NOTEDATA":
                if partial_chart is not None:
                    self.charts.append(partial_chart)
                partial_chart = SSCChart()
            elif partial_chart is not None:
                partial_chart._properties[key] = value or ""
            else:
                self._properties[key] = value or ""
        if partial_chart is not None:
            self.charts.append(partial_chart)

    @property
    def charts(self) -> SSCCharts:
        return self._charts

    @charts.setter
    def charts(self, charts: Sequence[SSCChart]):
        self._charts = SSCCharts(charts)
