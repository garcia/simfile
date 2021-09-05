"""
Simfile & chart classes for SSC files.
"""
from typing import Optional, Type

from msdparser import parse_msd

from .base import BaseChart, BaseCharts, BaseSimfile, MSD_ITERATOR
from ._private.dedent import dedent_and_trim
from ._private.property import item_property


__all__ = ['SSCChart', 'SSCCharts', 'SSCSimfile']


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
    chartname = item_property('CHARTNAME')
    chartstyle = item_property('CHARTSTYLE')
    credit = item_property('CREDIT')
    music = item_property('MUSIC')
    bpms = item_property('BPMS')
    stops = item_property('STOPS')
    delays = item_property('DELAYS')
    timesignatures = item_property('TIMESIGNATURES')
    tickcounts = item_property('TICKCOUNTS')
    combos = item_property('COMBOS')
    warps = item_property('WARPS')
    speeds = item_property('SPEEDS')
    scrolls = item_property('SCROLLS')
    fakes = item_property('FAKES')
    labels = item_property('LABELS')
    attacks = item_property('ATTACKS')
    offset = item_property('OFFSET')
    displaybpm = item_property('DISPLAYBPM')

    # "NOTES2" alias only supported by SSC files
    notes = item_property('NOTES', alias='NOTES2')

    @classmethod
    def from_str(
        cls: Type['SSCChart'],
        string: str,
        strict: bool = True
    ) -> 'SSCChart':
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
    def blank(cls: Type['SSCChart']) -> 'SSCChart':
        return cls.from_str("""
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
        """)
    
    def _parse(self, parser: MSD_ITERATOR) -> None:
        iterator = iter(parser)
        
        first_key, _ = next(iterator)
        if first_key.upper() != 'NOTEDATA':
            raise ValueError('expected NOTEDATA property first')
        
        for key, value in iterator:
            self[key] = value
            if value is self.notes:
                break

    def serialize(self, file):
        file.write('#NOTEDATA:;\n')
        notes_key = 'NOTES'
        for (key, value) in self.items():
            # notes must always be the last property in a chart
            if value is self.notes:
                notes_key = key
                continue
            file.write(f'#{key}:{value};\n')
        file.write(f'#{notes_key}:{self[notes_key]};\n\n')


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
    
    version = item_property('VERSION')
    origin = item_property('ORIGIN')
    previewvid = item_property('PREVIEWVID')
    jacket = item_property('JACKET')
    cdimage = item_property('CDIMAGE')
    discimage = item_property('DISCIMAGE')
    preview = item_property('PREVIEW')
    musiclength = item_property('MUSICLENGTH')
    lastsecondhint = item_property('LASTSECONDHINT')
    warps = item_property('WARPS')
    labels = item_property('LABELS')
    combos = item_property('COMBOS')
    speeds = item_property('SPEEDS')
    scrolls = item_property('SCROLLS')
    fakes = item_property('FAKES')

    @classmethod
    def blank(cls: Type['SSCSimfile']) -> 'SSCSimfile':
        return SSCSimfile(string=dedent_and_trim("""
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
        """))

    def _parse(self, parser):
        self._charts = SSCCharts()
        partial_chart: Optional[SSCChart] = None
        for key, value in parser:
            key = key.upper()            
            if key == 'NOTEDATA':
                if partial_chart is not None:
                    self._charts.append(partial_chart)
                partial_chart = SSCChart()
            elif partial_chart is not None:
                partial_chart[key] = value
            else:
                self[key] = value
        if partial_chart is not None:
            self._charts.append(partial_chart)
    
    @property
    def charts(self) -> SSCCharts:
        return self._charts
