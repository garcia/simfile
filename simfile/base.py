from abc import ABCMeta, abstractmethod
from collections import OrderedDict, UserList
from typing import Any, FrozenSet, Iterator, Mapping, Optional, TextIO, Union

from msdparser import MSDParser

from ._private.serializable import Serializable
from ._private.generic import E, ListWithRepr


__all__ = ['BaseChart', 'BaseCharts', 'BaseSimfile']


class BaseChart(Serializable, metaclass=ABCMeta):
    """
    One chart from a simfile.
    """
    @property
    @abstractmethod
    def stepstype(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def difficulty(self) -> str:
        pass

    @property
    @abstractmethod
    def meter(self) -> int:
        pass

    @property
    @abstractmethod
    def radarvalues(self) -> str:
        pass

    @property
    @abstractmethod
    def notes(self) -> str:
        pass
    
    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f'<{cls}: {self.stepstype} {self.difficulty} {self.meter}>'


class BaseCharts(ListWithRepr[E], Serializable, metaclass=ABCMeta):
    """
    A list of BaseChart objects.
    """
    def __init__(self, data=None):
        super().__init__(data)

    @Serializable.enable_string_output
    def serialize(self, file: TextIO):
        for chart in self:
            chart.serialize(file)
            file.write('\n')


class BaseSimfile(OrderedDict, Serializable, metaclass=ABCMeta):
    """
    The BaseSimfile class encapsulates simfile parameters and charts.

    BaseSimfile objects can be created from filenames or file-like objects. They
    can also be created from strings containing simfile data using the
    `from_string` class method.

    Parameters are accessed through a dict-like interface. Identifiers are
    case-sensitive, but coerced to uppercase when importing. BaseCharts are stored
    in a `BaseCharts` object under the `charts` attribute.
    """
    def __init__(self, *,
                 file: Optional[Union[TextIO, Iterator[str]]] = None,
                 string: Optional[str] = None):
        if file is not None or string is not None:
            with MSDParser(file=file, string=string) as parser:
                self._parse(parser)
    
    @abstractmethod
    def _parse(self, parser: MSDParser):
        pass

    @Serializable.enable_string_output
    def serialize(self, file: TextIO):
        for (key, value) in self.items():
            file.write(f'#{key}:{value};\n')
        file.write('\n')
        self.charts.serialize(file)

    @property
    @abstractmethod
    def charts(self) -> BaseCharts:
        pass

    def __repr__(self):
        rtn = '<' + self.__class__.__name__
        if self.get('TITLE'):
            rtn += ': ' + self['TITLE']
            if self.get('SUBTITLE'):
                rtn += ' ' + self['SUBTITLE']
        return rtn + '>'

    def __eq__(self, other):
        """
        Test for equality with another BaseSimfile.

        Two simfiles are equal if they have the same type, parameters, and
        charts.
        """
        return (type(self) is type(other) and
                OrderedDict.__eq__(self, other) and
                self.charts == other.charts)
    
    def __ne__(self, other):
        """
        Test for inequality with another BaseSimfile.
        """
        return not self.__eq__(other)
                