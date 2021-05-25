from typing import List, Optional, Type

from msdparser.msdparser import MSDParser

from .base import BaseChart, BaseCharts, BaseSimfile
from ._private.dedent import dedent_and_trim


__all__ = ['SMChart', 'SMCharts', 'SMSimfile']


SM_CHART_PROPERTIES = (
    'STEPSTYPE', 'DESCRIPTION', 'DIFFICULTY', 'METER', 'RADARVALUES', 'NOTES',
)


class SMChart(BaseChart):
    """
    SM implementation of :class:`~simfile.base.BaseChart`.

    Unlike :class:`~simfile.ssc.SSCChart`, SM chart metadata is stored
    as a fixed list of 6 properties, so this class prohibits adding or
    deleting keys from its backing OrderedDict.
    """
    
    extradata: Optional[List[str]] = None
    """
    If the chart data contains more than 6 components, the extra
    components will be stored in this attribute.
    """
    
    @classmethod
    def blank(cls: Type['SMChart']) -> 'SMChart':
        return SMChart.from_str(dedent_and_trim("""
                 dance-single:
                 :
                 Beginner:
                 1:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000
        """))

    @classmethod
    def from_str(cls: Type['SMChart'], string: str) -> 'SMChart':
        """
        Parse the MSD value component of a NOTES property.

        The string should contain six colon-separated components,
        corresponding to each of the base known properties documented
        in :class:`simfile.base.BaseChart`. Any additional components
        will be stored in :data:`extradata`.

        Raises :code:`ValueError` if the string contains fewer than six
        components.
        """
        instance = cls()
        instance._from_str(string)
        return instance
    
    def _from_str(self, string: str) -> None:
        values = string.split(':')
        if len(values) < len(SM_CHART_PROPERTIES):
            raise ValueError(
                f'expected at least {len(SM_CHART_PROPERTIES)} '
                f'chart components, got {len(values)}'
            )
        
        for property, value in zip(SM_CHART_PROPERTIES, values):
            self[property] = value.strip()
        
        if len(values) > len(SM_CHART_PROPERTIES):
            self.extradata = values[len(SM_CHART_PROPERTIES):]
    
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
            f'{":" + ":".join(self.extradata) if self.extradata else ""}'
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
        """Raises NotImplementedError."""
        # This could be implemented, but I don't see a use case
        raise NotImplementedError

    def pop(self, property, default=None):
        """Raises NotImplementedError.""" 
        raise NotImplementedError
    
    def popitem(self, last=True):
        """Raises NotImplementedError."""
        raise NotImplementedError
    
    def __getitem__(self, property):
        if property in SM_CHART_PROPERTIES:
            return getattr(self, property.lower())
        else:
            raise KeyError

    def __setitem__(self, property: str, value: str) -> None:
        if property.upper() not in SM_CHART_PROPERTIES:
            raise KeyError
        else:
            return super().__setitem__(property, value)

    def __delitem__(self, property: str) -> None:
        """Raises NotImplementedError."""
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
    _charts: SMCharts

    def _parse(self, parser: MSDParser):
        self._charts = SMCharts()
        for (key, value) in parser:
            key = key.upper()
            if key == 'NOTES':
                self._charts.append(SMChart.from_str(value))
            else:
                self[key] = value
    
    @classmethod
    def blank(cls: Type['SMSimfile']) -> 'SMSimfile':
        return SMSimfile(string=dedent_and_trim("""
            #TITLE:;
            #SUBTITLE:;
            #ARTIST:;
            #TITLETRANSLIT:;
            #SUBTITLETRANSLIT:;
            #ARTISTTRANSLIT:;
            #GENRE:;
            #CREDIT:;
            #BANNER:;
            #BACKGROUND:;
            #LYRICSPATH:;
            #CDTITLE:;
            #MUSIC:;
            #OFFSET:0.000000;
            #SAMPLESTART:100.000000;
            #SAMPLELENGTH:12.000000;
            #SELECTABLE:YES;
            #BPMS:0.000000=60.000000;
            #STOPS:;
            #BGCHANGES:;
            #KEYSOUNDS:;
            #ATTACKS:;
        """))
    
    @property
    def charts(self) -> SMCharts:
        return self._charts
