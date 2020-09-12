from collections import OrderedDict
from typing import Optional

from .base import BaseChart, BaseCharts, BaseSimfile
from msdparser import MSDParser


__all__ = ['SSCChart', 'SSCCharts', 'SSCSimfile']


def _chart_property(name):

    @property
    def chart_property(self):
        return self[name]

    @chart_property.setter
    def chart_property(self, value):
        self[name] = value

    return chart_property


class SSCChart(BaseChart, OrderedDict):
    chartname = _chart_property('CHARTNAME')
    stepstype = _chart_property('STEPSTYPE')
    description = _chart_property('DESCRIPTION')
    chartstyle = _chart_property('CHARTSTYLE')
    difficulty = _chart_property('DIFFICULTY')
    meter = _chart_property('METER')
    radarvalues = _chart_property('RADARVALUES')
    credit = _chart_property('CREDIT')
    displaybpm = _chart_property('DISPLAYBPM')
    notes = _chart_property('NOTES')

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
