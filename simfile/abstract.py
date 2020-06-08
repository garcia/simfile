from abc import ABC, abstractmethod
from typing import Collection, Generator, Mapping, NewType, Sequence

MsdParameter = NewType('MsdParameter', Sequence[str])
MsdGenerator = NewType('MsdGenerator', Generator[MsdParameter, None, None])

class ListWithRepr(list):
    """
    Subclass of 'list' that overrides __repr__.
    """
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super().__repr__())

class MSDEncodable(ABC):
    @abstractmethod
    def to_msd(self) -> MsdGenerator:
        pass

    @classmethod
    @abstractmethod
    def from_msd(cls, msd: MsdGenerator):
        pass

    @classmethod
    def from_msd_parameter(cls, msd_parameter: MsdParameter):
        return cls.from_msd(iter((msd_parameter,)))

class MSDParameterEncodable(ABC):
    @abstractmethod
    def to_msd_values(self) -> MsdParameter:
        pass

    @classmethod
    @abstractmethod
    def from_msd_values(cls, msd_values: MsdParameter):
        pass

    @classmethod
    def from_msd_value(cls, msd_value: str):
        return cls.from_msd_values(iter((msd_value,)))

class Simfile(MSDEncodable):
    """
    The Simfile class encapsulates simfile parameters and charts.

    Simfile objects can be created from filenames or file-like objects. They
    can also be created from strings containing simfile data using the
    `from_string` class method.

    Parameters are accessed through a dict-like interface. Identifiers are
    case-sensitive, but coerced to uppercase when importing. Charts are stored
    in a `Charts` object under the `charts` attribute.
    """
    @classmethod
    @abstractmethod
    def from_string(cls, string):
        pass

    @abstractmethod
    def save(self, filename=None):
        pass

    @property
    @abstractmethod
    def filename(self):
        pass

    @property
    @abstractmethod
    def parameters(self):
        pass

    @property
    @abstractmethod
    def charts(self):
        pass

    @property
    @abstractmethod
    def title(self):
        pass

    @property
    @abstractmethod
    def subtitle(self):
        pass

    @property
    @abstractmethod
    def artist(self):
        pass

    @property
    @abstractmethod
    def titletranslit(self):
        pass

    @property
    @abstractmethod
    def subtitletranslit(self):
        pass

    @property
    @abstractmethod
    def artisttranslit(self):
        pass

    @property
    @abstractmethod
    def music(self):
        pass

    @property
    @abstractmethod
    def samplestart(self):
        pass

    @property
    @abstractmethod
    def samplelength(self):
        pass

    @property
    @abstractmethod
    def bpms(self):
        pass

    @property
    @abstractmethod
    def stops(self):
        pass

    @property
    @abstractmethod
    def offset(self):
        pass

    @property
    @abstractmethod
    def credit(self):
        pass

    @property
    @abstractmethod
    def genre(self):
        pass

    @property
    @abstractmethod
    def displaybpm(self):
        pass

class Parameters(MSDEncodable, Mapping):
    pass

class Charts(MSDEncodable, Sequence):
    @property
    @abstractmethod
    def supported_fields(self):
        pass

    def _match(self, chart, fields):
        for field, value in fields.items():
            if getattr(chart, field) != value:
                return False
        return True

    def filter(self, **fields):
        """
        Filter charts and return matches in a new Charts object.

        If no charts match the given criteria, returns an empty Charts object.
        """
        unsupported_fields = set(fields.keys()) - self.supported_fields
        if unsupported_fields:
            raise KeyError('unsupported fields:', unsupported_fields)
        result = self.__class__()
        for chart in self:
            if self._match(chart, fields):
                result.append(chart)
        return result

    def get(self, **fields):
        """
        Get a chart that matches the given criteria.

        Arguments are identical to those of `filter`. Raises ``LookupError``
        if any number of charts other than one are matched.
        """
        result = self.filter(**fields)
        if len(result) != 1:
            raise LookupError('%s charts match the given parameters' %
                              len(result))
        return result[0]

class Chart(MSDEncodable):
    @property
    @abstractmethod
    def stepstype(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def difficulty(self):
        pass

    @property
    @abstractmethod
    def meter(self):
        pass

    @property
    @abstractmethod
    def radar(self):
        pass

    @property
    @abstractmethod
    def notes(self):
        pass

class Notes(MSDParameterEncodable, Sequence):
    pass