from abc import ABCMeta, abstractmethod
from collections import OrderedDict, UserList
from typing import Any, FrozenSet, Iterator, Mapping, Optional, TextIO, Union

from msdparser import MSDParser

from ._private.generic import E, ListWithRepr
from ._private.property import item_property
from ._private.serializable import Serializable


__all__ = ['BaseChart', 'BaseCharts', 'BaseSimfile']


class BaseChart(Serializable, metaclass=ABCMeta):
    """
    One chart from a simfile.

    All charts have the following string properties: `stepstype`,
    `description`, `difficulty`, `meter`, `radarvalues`, and `notes`.
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
    List containing all of a simfile's charts.
    """
    def __init__(self, data=None):
        super().__init__(data)

    def serialize(self, file: TextIO):
        for chart in self:
            chart.serialize(file)
            file.write('\n')


class BaseSimfile(OrderedDict, Serializable, metaclass=ABCMeta):
    """
    A simfile, including its metadata (e.g. song title) and charts.

    Metadata is stored directly on the simfile object through a
    dict-like interface. Keys are unique (if there are duplicates, the
    last value wins) and converted to uppercase.
    
    Additionally, properties recognized by the current stable version
    of StepMania are exposed through lower-case properties on the
    object for easy (and implicitly spell-checked) access. The
    following properties are defined:

    * Song metadata: `title`, `subtitle`, `artist`, `titletranslit`,
      `subtitletranslit`, `artisttranslit`, `genre`
    * Simfile metadata: `credit`, `samplestart`, `samplelength`,
      `selectable`, `bgchanges`, `keysounds`, `attacks`
    * Relative file paths: `banner`, `background`, `lyricspath`,
      `cdtitle`, `music`
    * Timing data: `offset`, `bpms`, `stops`

    If a desired simfile property isn't in this list, it can still be
    accessed as a dict item.
    """
    title = item_property('TITLE')
    subtitle = item_property('SUBTITLE')
    artist = item_property('ARTIST')
    titletranslit = item_property('TITLETRANSLIT')
    subtitletranslit = item_property('SUBTITLETRANSLIT')
    artisttranslit = item_property('ARTISTTRANSLIT')
    genre = item_property('GENRE')
    credit = item_property('CREDIT')
    banner = item_property('BANNER')
    background = item_property('BACKGROUND')
    lyricspath = item_property('LYRICSPATH')
    cdtitle = item_property('CDTITLE')
    music = item_property('MUSIC')
    offset = item_property('OFFSET')
    samplestart = item_property('SAMPLESTART')
    samplelength = item_property('SAMPLELENGTH')
    selectable = item_property('SELECTABLE')
    bpms = item_property('BPMS')
    stops = item_property('STOPS')
    bgchanges = item_property('BGCHANGES')
    keysounds = item_property('KEYSOUNDS')
    attacks = item_property('ATTACKS')

    def __init__(self, *,
                 file: Optional[Union[TextIO, Iterator[str]]] = None,
                 string: Optional[str] = None):
        if file is not None or string is not None:
            with MSDParser(file=file, string=string) as parser:
                self._parse(parser)
    
    @abstractmethod
    def _parse(self, parser: MSDParser):
        pass

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
                