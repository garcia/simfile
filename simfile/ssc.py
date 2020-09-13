from collections import OrderedDict
from typing import Optional

from msdparser import MSDParser

from .base import BaseChart, BaseCharts, BaseSimfile
from ._private.property import item_property


__all__ = ['SSCChart', 'SSCCharts', 'SSCSimfile']


class SSCChart(BaseChart, OrderedDict):
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

    def serialize(self, file):
        file.write('#NOTEDATA:;\n')
        for (key, value) in self.items():
            file.write(f'#{key}:{value};\n')
        file.write('\n')


class SSCCharts(BaseCharts):

    @property
    def supported_fields(self):
        return frozenset({'chartname', 'stepstype', 'description',
                          'chartstyle', 'difficulty', 'meter', 'radarvalues',
                          'credit', 'displaybpm'})


class SSCSimfile(BaseSimfile):

    def _parse(self):
        with MSDParser(file=self.file, string=self.string) as parser:
            self._charts = SSCCharts()
            partial_chart: Optional[SSCChart] = None
            for (key, value) in parser:
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
