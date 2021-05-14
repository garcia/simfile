from collections import UserDict
from collections.abc import Mapping

from msdparser.msdparser import MSDParser

from .base import BaseChart, BaseCharts, BaseSimfile
from ._private.property import item_property
from ._private.serializable import Serializable


__all__ = ['SMChart', 'SMCharts', 'SMSimfile']


SM_CHART_PROPERTIES = (
    'STEPSTYPE', 'DESCRIPTION', 'DIFFICULTY', 'METER', 'RADARVALUES', 'NOTES',
)


class SMChart(BaseChart):
    """
    SM implementation of :class:`~simfile.base.BaseChart`.
    """
    
    def _from_str(self, string: str) -> None:
        values = string.split(':')
        if len(values) != len(SM_CHART_PROPERTIES):
            raise ValueError(
                f'expected {len(SM_CHART_PROPERTIES)} chart components, '
                f'got {len(values)}'
            )
        
        for property, value in zip(SM_CHART_PROPERTIES, values):
            self[property] = value.strip()

    @classmethod
    def from_str(cls, string: str) -> 'SMChart':
        instance = cls()
        instance._from_str(string)
        return instance
    
    def _parse(self, parser: MSDParser):
        property, value = next(iter(parser))
        if property.upper() != 'NOTES':
            raise ValueError(f'expected a NOTES property, got {property}')
        
        self._from_str(value)

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

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.stepstype == other.stepstype and
                self.description == other.description and
                self.difficulty == other.difficulty and
                self.meter == other.meter and
                self.radarvalues == other.radarvalues and
                self.notes == other.notes)
    
    # Prevent keys from being added or removed
    
    def update(self, *args, **kwargs) -> None:
        # This could be implemented, but I don't see a use case
        raise NotImplementedError

    def pop(self, property, default=None):
        raise NotImplementedError
    
    def popitem(self, last=True):
        raise NotImplementedError
    
    def __getitem__(self, property):
        if property.upper() in SM_CHART_PROPERTIES:
            return getattr(self, property)
        else:
            raise KeyError

    def __setitem__(self, property: str, value: str) -> None:
        if property.upper() not in SM_CHART_PROPERTIES:
            raise KeyError
        else:
            return super().__setitem__(property, value)

    def __delitem__(self, property: str) -> None:
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

    def _parse(self, parser: MSDParser):
        self._charts = SMCharts()
        for (key, value) in parser:
            key = key.upper()
            if key == 'NOTES':
                self._charts.append(SMChart.from_str(value))
            else:
                self[key] = value
    
    @property
    def charts(self):
        return self._charts
