from abc import ABCMeta, abstractmethod
from collections import OrderedDict, UserList
from typing import Any, Collection, FrozenSet, Generator, Mapping, NewType, \
                   Optional, Sequence, TextIO


__all__ = ['Chart', 'Charts', 'Simfile']


class ListWithRepr(UserList):
    """
    Subclass of UserLis that overrides __repr__.
    """
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super().__repr__())


class Serializable(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self, file):
        pass


class Chart(Serializable, metaclass=ABCMeta):
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


class Charts(ListWithRepr, Serializable, metaclass=ABCMeta):
    """
    A filterable list of Chart objects.
    """
    @property
    @abstractmethod
    def supported_fields(self) -> FrozenSet[str]:
        pass

    def _match(self, chart: Chart, fields: Mapping[str, Any]):
        for field, value in fields.items():
            if getattr(chart, field) != value:
                return False
        return True

    def filter(self, **fields: Any):
        """
        Filter charts according to the provided field values.
        
        All provided fields must be present in the implementation's
        `supported_fields()`, otherwise KeyError will be raised.

        In order for a chart to be yielded, all fields must exactly match
        the provided value.
        """
        unsupported_fields = set(fields.keys()) - self.supported_fields
        if unsupported_fields:
            raise KeyError('unsupported fields:', unsupported_fields)
        for chart in self:
            if self._match(chart, fields):
                yield chart

    def get(self, **fields: Any):
        """
        Get a chart that matches the given criteria.

        Arguments are identical to those of `filter`. Raises ``LookupError``
        if any number of charts other than one are matched.
        """
        generator = self.filter(**fields)

        try:
            match = next(generator)
        except StopIteration:
            raise LookupError('no charts match these parameters')

        try:
            next(generator)
        except StopIteration:
            return match

        raise LookupError('multiple charts match these parameters')

    def serialize(self, file):
        for chart in self:
            chart.serialize(file)
            file.write('\n')


class Simfile(OrderedDict, Serializable, metaclass=ABCMeta):
    """
    The Simfile class encapsulates simfile parameters and charts.

    Simfile objects can be created from filenames or file-like objects. They
    can also be created from strings containing simfile data using the
    `from_string` class method.

    Parameters are accessed through a dict-like interface. Identifiers are
    case-sensitive, but coerced to uppercase when importing. Charts are stored
    in a `Charts` object under the `charts` attribute.
    """
    def __init__(self, *,
                 file: Optional[TextIO] = None,
                 string: Optional[str] = None):
        if file is None and string is None:
            raise ValueError("must provide either a file or a string")
        if file is not None and string is not None:
            raise ValueError("must provide either a file or a string, not both")
        self.file = file
        self.string = string
        self._parse()
    
    @abstractmethod
    def _parse(self):
        pass

    def serialize(self, file):
        for (key, value) in self.items():
            file.write(f'#{key}:{value};\n')
        file.write('\n')
        self.charts.serialize(file)

    @property
    @abstractmethod
    def charts(self) -> Sequence[Charts]:
        pass

    def __repr__(self):
        rtn = '<' + self.__class__.__name__
        if 'TITLE' in self:
            rtn += ': ' + self['TITLE']
            if 'SUBTITLE' in self:
                rtn += ' ' + self['SUBTITLE']
        return rtn + '>'

    def __eq__(self, other):
        """
        Test for equality with another Simfile.

        Two simfiles are equal if they have the same type, parameters, and
        charts.
        """
        return (type(self) is type(other) and
                super(OrderedDict, self) == super(OrderedDict, other) and
                self.charts == other.charts)