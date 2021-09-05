"""
Base classes for simfile & chart implementations.

This module should ideally never need to be used directly, but its
documentation may be useful for understanding the similarities between
the SM and SSC formats.
"""
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
      `samplestart`, `samplelength`, `selectable`, `instrumenttrack`,
      `timesignatures`
    * File paths: `banner`, `background`, `lyricspath`, `cdtitle`,
      `music`
    * Gameplay events: `bgchanges`, `fgchanges`, `keysounds`, `attacks`,
      `tickcounts`
    * Timing data: `offset`, `bpms`, `stops`, `delays`

    If a desired simfile property isn't in this list, it can still be
    accessed as a dict item.

    By default, the underlying parser will throw an exception if it
    finds any stray text between parameters. This behavior can be
    overridden by setting `strict` to False in the constructor.
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
    bpms = item_property('BPMS')
    stops = item_property('STOPS')
    delays = item_property('DELAYS')
    timesignatures = item_property('TIMESIGNATURES')
    tickcounts = item_property('TICKCOUNTS')
    instrumenttrack = item_property('INSTRUMENTTRACK')
    samplestart = item_property('SAMPLESTART')
    samplelength = item_property('SAMPLELENGTH')
    displaybpm = item_property('DISPLAYBPM')
    selectable = item_property('SELECTABLE')
    bgchanges = item_property('BGCHANGES', alias='ANIMATIONS')
    fgchanges = item_property('FGCHANGES')
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
        if self.title:
            rtn += ': ' + self.title
            if self.subtitle:
                rtn += ' ' + self.subtitle
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
                