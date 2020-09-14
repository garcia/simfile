from .base import BaseChart, BaseCharts, BaseSimfile
from ._private.property import attr_property
from ._private.serializable import Serializable


__all__ = ['SMChart', 'SMCharts', 'SMSimfile']


class SMChart(BaseChart):
    """
    SM implementation of :class:`~simfile.base.BaseChart`.
    """
    stepstype = attr_property('_stepstype', str)
    description = attr_property('_description', str)
    difficulty = attr_property('_difficulty', str)
    meter = attr_property('_meter', str)
    radarvalues = attr_property('_radarvalues', str)
    notes = attr_property('_notes', str)

    def serialize(self, file):
        file.write(
            f'#NOTES:\n'
            f'     {self.stepstype}:\n'
            f'     {self.description}:\n'
            f'     {self.difficulty}:\n'
            f'     {self.meter}:\n'
            f'     {self.radarvalues}:\n'
            f'{self.notes}\n'
            f';'
        )

    def __init__(self, string: str):
        values = string.split(':')
        if len(values) != 6:
            raise ValueError(f'expected 6 chart components, got {len(values)}')
        iterator = iter(values)
        self.stepstype = next(iterator).strip()
        self.description = next(iterator).strip()
        self.difficulty = next(iterator).strip()
        self.meter = next(iterator).strip()
        self.radarvalues = next(iterator).strip()
        self.notes = next(iterator).strip()

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.stepstype == other.stepstype and
                self.description == other.description and
                self.difficulty == other.difficulty and
                self.meter == other.meter and
                self.radarvalues == other.radarvalues and
                self.notes == other.notes)


class SMCharts(BaseCharts[SMChart]):
    """
    SM implementation of :class:`~simfile.base.BaseCharts`.

    List elements are :class:`SMChart` instances.
    """
    @property
    def supported_fields(self):
        return frozenset({'stepstype', 'description', 'difficulty', 'meter', 'radarvalues'})


class SMSimfile(BaseSimfile):
    """
    SM implementation of :class:`~simfile.base.BaseSimfile`.
    """

    def _parse(self, parser):
        self._charts = SMCharts()
        for (key, value) in parser:
            key = key.upper()
            if key == 'NOTES':
                self._charts.append(SMChart(string=value))
            else:
                self[key] = value
    
    @property
    def charts(self):
        return self._charts
