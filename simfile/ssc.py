from collections import OrderedDict
from typing import Optional

from msdparser.msdparser import MSDParser

from .base import BaseChart, BaseCharts, BaseSimfile
from ._private.property import item_property
from ._private.serializable import Serializable


__all__ = ['SSCChart', 'SSCCharts', 'SSCSimfile']


class SSCChart(BaseChart, OrderedDict):
    """
    SSC implementation of :class:`~simfile.base.BaseChart`.

    Unlike :class:`~simfile.sm.SMChart`, SSC chart metadata is stored
    as key-value pairs, so this class acts extends OrderedDict for its
    attributes. All named properties are backed by this OrderedDict.

    Adds the following known properties: `chartname`, `chartstyle`,
    `credit`, and `displaybpm`.
    """
    chartname = item_property('CHARTNAME')
    stepstype = item_property('STEPSTYPE')
    description = item_property('DESCRIPTION')
    chartstyle = item_property('CHARTSTYLE')
    difficulty = item_property('DIFFICULTY')
    meter = item_property('METER')
    radarvalues = item_property('RADARVALUES')
    credit = item_property('CREDIT')
    displaybpm = item_property('DISPLAYBPM')
    notes = item_property('NOTES')

    def _parse(self, parser: MSDParser) -> None:
        iterator = iter(parser)
        
        first_key, _ = next(iterator)
        if first_key.upper() != 'NOTEDATA':
            raise ValueError()
        
        for key, value in iterator:
            self[key] = value
            if key.upper() == 'NOTES':
                break

    def serialize(self, file):
        file.write('#NOTEDATA:;\n')
        for (key, value) in self.items():
            file.write(f'#{key}:{value};\n')
        file.write('\n')


class SSCCharts(BaseCharts[SSCChart]):
    """
    SSC implementation of :class:`~simfile.base.BaseCharts`.

    List elements are :class:`SSCChart` instances.
    """
    pass


class SSCSimfile(BaseSimfile):
    """
    SSC implementation of :class:`~simfile.base.BaseSimfile`.

    Adds the following known properties:
    
    * SSC version: `version`
    * Song metadata: `origin`
    * Relative file paths: `previewvid`, `jacket`, `cdimage`,
      `discimage`
    * Timed gameplay events: `delays`, `warps`, `timesignatures`,
      `tickcounts`, `combos`, `speeds`, `scrolls`, `fakes`, `labels`
    """
    version = item_property('VERSION')
    origin = item_property('ORIGIN')
    previewvid = item_property('PREVIEWVID')
    jacket = item_property('JACKET')
    cdimage = item_property('CDIMAGE')
    discimage = item_property('DISCIMAGE')
    delays = item_property('DELAYS')
    warps = item_property('WARPS')
    timesignatures = item_property('TIMESIGNATURES')
    tickcounts = item_property('TICKCOUNTS')
    combos = item_property('COMBOS')
    speeds = item_property('SPEEDS')
    scrolls = item_property('SCROLLS')
    fakes = item_property('FAKES')
    labels = item_property('LABELS')

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
    def charts(self):
        return self._charts
