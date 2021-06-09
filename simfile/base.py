from abc import ABCMeta, abstractclassmethod, abstractmethod
from collections import OrderedDict
from typing import Iterator, Optional, TextIO, Tuple, Union

from msdparser import parse_msd

from ._private.generic import E, ListWithRepr
from ._private.property import item_property
from ._private.serializable import Serializable


__all__ = ['BaseChart', 'BaseCharts', 'BaseSimfile']


MSD_ITERATOR = Iterator[Tuple[str, str]]


class BaseChart(OrderedDict, Serializable, metaclass=ABCMeta):
    """
    One chart from a simfile.

    All charts have the following known properties: `stepstype`,
    `description`, `difficulty`, `meter`, `radarvalues`, and `notes`.
    """
    stepstype = item_property('STEPSTYPE')
    description = item_property('DESCRIPTION')
    difficulty = item_property('DIFFICULTY')
    meter = item_property('METER')
    radarvalues = item_property('RADARVALUES')
    notes = item_property('NOTES')
    
    @abstractmethod
    def _parse(self, parser: MSD_ITERATOR):
        pass

    @abstractclassmethod
    def blank(cls):
        """
        Generate a blank, valid chart populated with standard keys.

        This should approximately match blank charts produced by the
        StepMania editor. 
        """

    def __repr__(self) -> str:
        """
        Pretty repr() for charts.
        
        Includes the class name, stepstype, difficulty, and meter.
        """
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
    following known properties are defined:

    * Metadata: `title`, `subtitle`, `artist`, `titletranslit`,
      `subtitletranslit`, `artisttranslit`, `genre`, `credit`,
      `samplestart`, `samplelength`, `selectable`, 
    * File paths: `banner`, `background`, `lyricspath`, `cdtitle`,
      `music`
    * Gameplay events: `bgchanges`, `keysounds`, `attacks`
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
    displaybpm = item_property('DISPLAYBPM')
    bpms = item_property('BPMS')
    stops = item_property('STOPS')
    bgchanges = item_property('BGCHANGES')
    keysounds = item_property('KEYSOUNDS')
    attacks = item_property('ATTACKS')

    def __init__(self, *,
                 file: Optional[Union[TextIO, Iterator[str]]] = None,
                 string: Optional[str] = None,
                 strict: bool = True):
        if file is not None or string is not None:
            self._parse(parse_msd(
                file=file,
                string=string,
                ignore_stray_text=not strict,
            ))
    
    @abstractmethod
    def _parse(self, parser: MSD_ITERATOR):
        pass
    
    @abstractclassmethod
    def blank(cls):
        """
        Generate a blank, valid simfile populated with standard keys.

        This should approximately match the simfile produced by the
        StepMania editor in a directory with no .sm or .ssc files. 
        """

    def serialize(self, file: TextIO):
        for (key, value) in self.items():
            file.write(f'#{key}:{value};\n')
        file.write('\n')
        self.charts.serialize(file)

    @property
    @abstractmethod
    def charts(self):
        """
        List of charts associated with this simfile.
        """

    def __repr__(self) -> str:
        """
        Pretty repr() for simfiles.

        Includes the class name, title, and subtitle.
        """
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
                