from copy import deepcopy
import itertools
from typing import (
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

from simfile.sm import SMChart, SMSimfile
from simfile.ssc import SSCChart, SSCSimfile
from simfile.types import Chart, Simfile


__all__ = ["FakeObject", "FakeChart", "FakeSimfile"]


class FakeObject:
    @classmethod
    def maybe_set(cls, obj, attr, value):
        if value is not None and hasattr(obj, attr):
            setattr(obj, attr, value)


ChartType = Union[Type[SMChart], Type[SSCChart]]
CT = TypeVar("CT", Type[SMChart], Type[SSCChart])
C = TypeVar("C", SMChart, SSCChart)


class FakeChart(FakeObject):
    @classmethod
    def make_blank(
        cls, chart_types: Sequence[ChartType] = (SMChart, SSCChart)
    ) -> List[Chart]:
        return [ct.blank() for ct in chart_types]

    def __init__(self, chart_types: Sequence[ChartType] = (SMChart, SSCChart)):
        self.charts = FakeChart.make_blank(chart_types=chart_types)

    def with_fields(
        self,
        *,
        combinations=False,
        stepstype: Optional[str] = None,
        description: Optional[str] = None,
        difficulty: Optional[str] = None,
        meter: Optional[str] = None,
        radarvalues: Optional[str] = None,
        notes: Optional[str] = None,
        chartname: Optional[str] = None,
        chartstyle: Optional[str] = None,
        credit: Optional[str] = None,
        music: Optional[str] = None,
        bpms: Optional[str] = None,
        stops: Optional[str] = None,
        delays: Optional[str] = None,
        timesignatures: Optional[str] = None,
        tickcounts: Optional[str] = None,
        combos: Optional[str] = None,
        warps: Optional[str] = None,
        speeds: Optional[str] = None,
        scrolls: Optional[str] = None,
        fakes: Optional[str] = None,
        labels: Optional[str] = None,
        attacks: Optional[str] = None,
        offset: Optional[str] = None,
        displaybpm: Optional[str] = None,
    ):
        orig_charts: Optional[List[Chart]] = (
            [deepcopy(s) for s in self.charts] if combinations else None
        )

        for chart in self.charts:
            self.maybe_set(chart, "stepstype", stepstype)
            self.maybe_set(chart, "description", description)
            self.maybe_set(chart, "difficulty", difficulty)
            self.maybe_set(chart, "meter", meter)
            self.maybe_set(chart, "radarvalues", radarvalues)
            self.maybe_set(chart, "notes", notes)
            self.maybe_set(chart, "chartname", chartname)
            self.maybe_set(chart, "chartstyle", chartstyle)
            self.maybe_set(chart, "credit", credit)
            self.maybe_set(chart, "music", music)
            self.maybe_set(chart, "bpms", bpms)
            self.maybe_set(chart, "stops", stops)
            self.maybe_set(chart, "delays", delays)
            self.maybe_set(chart, "timesignatures", timesignatures)
            self.maybe_set(chart, "tickcounts", tickcounts)
            self.maybe_set(chart, "combos", combos)
            self.maybe_set(chart, "warps", warps)
            self.maybe_set(chart, "speeds", speeds)
            self.maybe_set(chart, "scrolls", scrolls)
            self.maybe_set(chart, "fakes", fakes)
            self.maybe_set(chart, "labels", labels)
            self.maybe_set(chart, "attacks", attacks)
            self.maybe_set(chart, "offset", offset)
            self.maybe_set(chart, "displaybpm", displaybpm)

        if orig_charts is not None:
            self.charts = list(
                itertools.chain.from_iterable(zip(orig_charts, self.charts))
            )

        return self

    def __iter__(self) -> Iterator[Chart]:
        yield from self.charts

    def of_type(self, chart_type: Union[CT, Type[C]]) -> Iterator[C]:
        yield from cast(
            Iterator[C], filter(lambda s: isinstance(s, chart_type), self.charts)
        )


SimfileType = Union[Type[SMSimfile], Type[SSCSimfile]]
ST = TypeVar("ST", Type[SMSimfile], Type[SSCSimfile])
S = TypeVar("S", SSCSimfile, SMSimfile)


class FakeSimfile(FakeObject):
    @classmethod
    def make_blank(
        cls, simfile_types: Iterable[SimfileType] = (SMSimfile, SSCSimfile)
    ) -> List[Simfile]:
        return [st.blank() for st in simfile_types]

    def __init__(
        self,
        simfile_types: Sequence[SimfileType] = (SMSimfile, SSCSimfile),
    ):
        self.simfiles = FakeSimfile.make_blank(simfile_types=simfile_types)

    def with_fields(
        self,
        *,
        combinations=False,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        artist: Optional[str] = None,
        titletranslit: Optional[str] = None,
        subtitletranslit: Optional[str] = None,
        artisttranslit: Optional[str] = None,
        genre: Optional[str] = None,
        credit: Optional[str] = None,
        banner: Optional[str] = None,
        background: Optional[str] = None,
        lyricspath: Optional[str] = None,
        cdtitle: Optional[str] = None,
        music: Optional[str] = None,
        offset: Optional[str] = None,
        bpms: Optional[str] = None,
        stops: Optional[str] = None,
        delays: Optional[str] = None,
        timesignatures: Optional[str] = None,
        tickcounts: Optional[str] = None,
        instrumenttrack: Optional[str] = None,
        samplestart: Optional[str] = None,
        samplelength: Optional[str] = None,
        displaybpm: Optional[str] = None,
        selectable: Optional[str] = None,
        bgchanges: Optional[str] = None,
        fgchanges: Optional[str] = None,
        keysounds: Optional[str] = None,
        attacks: Optional[str] = None,
        version: Optional[str] = None,
        origin: Optional[str] = None,
        previewvid: Optional[str] = None,
        jacket: Optional[str] = None,
        cdimage: Optional[str] = None,
        discimage: Optional[str] = None,
        preview: Optional[str] = None,
        musiclength: Optional[str] = None,
        lastsecondhint: Optional[str] = None,
        warps: Optional[str] = None,
        labels: Optional[str] = None,
        combos: Optional[str] = None,
        speeds: Optional[str] = None,
        scrolls: Optional[str] = None,
        fakes: Optional[str] = None,
        charts: Optional[FakeChart] = None,
    ):
        orig_simfiles: Optional[List[Simfile]] = (
            [deepcopy(s) for s in self.simfiles] if combinations else None
        )

        for simfile in self.simfiles:
            self.maybe_set(simfile, "title", title)
            self.maybe_set(simfile, "subtitle", subtitle)
            self.maybe_set(simfile, "artist", artist)
            self.maybe_set(simfile, "titletranslit", titletranslit)
            self.maybe_set(simfile, "subtitletranslit", subtitletranslit)
            self.maybe_set(simfile, "artisttranslit", artisttranslit)
            self.maybe_set(simfile, "genre", genre)
            self.maybe_set(simfile, "credit", credit)
            self.maybe_set(simfile, "banner", banner)
            self.maybe_set(simfile, "background", background)
            self.maybe_set(simfile, "lyricspath", lyricspath)
            self.maybe_set(simfile, "cdtitle", cdtitle)
            self.maybe_set(simfile, "music", music)
            self.maybe_set(simfile, "offset", offset)
            self.maybe_set(simfile, "bpms", bpms)
            self.maybe_set(simfile, "stops", stops)
            self.maybe_set(simfile, "delays", delays)
            self.maybe_set(simfile, "timesignatures", timesignatures)
            self.maybe_set(simfile, "tickcounts", tickcounts)
            self.maybe_set(simfile, "instrumenttrack", instrumenttrack)
            self.maybe_set(simfile, "samplestart", samplestart)
            self.maybe_set(simfile, "samplelength", samplelength)
            self.maybe_set(simfile, "displaybpm", displaybpm)
            self.maybe_set(simfile, "selectable", selectable)
            self.maybe_set(simfile, "bgchanges", bgchanges)
            self.maybe_set(simfile, "fgchanges", fgchanges)
            self.maybe_set(simfile, "keysounds", keysounds)
            self.maybe_set(simfile, "attacks", attacks)
            self.maybe_set(simfile, "version", version)
            self.maybe_set(simfile, "origin", origin)
            self.maybe_set(simfile, "previewvid", previewvid)
            self.maybe_set(simfile, "jacket", jacket)
            self.maybe_set(simfile, "cdimage", cdimage)
            self.maybe_set(simfile, "discimage", discimage)
            self.maybe_set(simfile, "preview", preview)
            self.maybe_set(simfile, "musiclength", musiclength)
            self.maybe_set(simfile, "lastsecondhint", lastsecondhint)
            self.maybe_set(simfile, "warps", warps)
            self.maybe_set(simfile, "labels", labels)
            self.maybe_set(simfile, "combos", combos)
            self.maybe_set(simfile, "speeds", speeds)
            self.maybe_set(simfile, "scrolls", scrolls)
            self.maybe_set(simfile, "fakes", fakes)
            if charts:
                simfile.charts.extend(
                    charts.of_type(
                        SMChart if isinstance(simfile, SMSimfile) else SSCChart
                    )
                )

        if orig_simfiles is not None:
            self.simfiles = list(
                itertools.chain.from_iterable(zip(orig_simfiles, self.simfiles))
            )

        return self

    def __iter__(self) -> Iterator[Simfile]:
        yield from self.simfiles

    def of_type(self, simfile_type: Union[ST, Type[S]]) -> Iterator[S]:
        yield from cast(
            Iterator[S], filter(lambda s: isinstance(s, simfile_type), self.simfiles)
        )
