from bisect import bisect
from collections import ChainMap, defaultdict
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction
from functools import total_ordering
from heapq import merge
from simfile.ssc import SSCChart
from typing import Iterable, MutableSequence, Type, NamedTuple

from ._private.generic import ListWithRepr
from .types import Simfile


__all__ = [
    'Beat', 'BeatEvent', 'BeatEvents', 'SongTime', 'TimingData',
    'TimingConverter',
]


MEASURE_SUBDIVISION = 192
BEAT_SUBDIVISION = MEASURE_SUBDIVISION // 4


class Beat(Fraction):
    """
    A fractional beat value, denoting vertical positioning / spacing in a
    simfile.
    """

    @classmethod
    def tick(cls) -> 'Beat':
        return cls(1, BEAT_SUBDIVISION)
    
    @classmethod
    def from_str(cls, beat_str) -> 'Beat':
        return Beat(beat_str).round_to_tick()
    
    def round_to_tick(self) -> 'Beat':
        return Beat(int(round(self * BEAT_SUBDIVISION)), BEAT_SUBDIVISION)
    
    def __str__(self):
        return f'{float(self):.3f}'
    
    def __repr__(self):
        return f'beat {self}'.rstrip('0').rstrip('.')


class BeatEvent(NamedTuple):
    """
    An event that occurs on a particular beat, e.g. a BPM change or stop.

    The decimal value's semantics vary based on the type of event:
    
    * BPMS: the new BPM value
    * STOPS, DELAYS: number of seconds to pause
    * WARPS: number of beats to skip
    """
    beat: Beat
    value: Decimal


class BeatEvents(ListWithRepr[BeatEvent]):
    """
    A list of :class:`BeatEvent` instances.
    """
    @classmethod
    def from_str(cls: Type['BeatEvents'], string: str) -> 'BeatEvents':
        instance = cls()
        
        if string.strip():
            for row in string.split(','):
                beat, value = row.strip().split('=')
                instance.append(BeatEvent(Beat.from_str(beat), Decimal(value)))
        
        return instance

    def serialize(self) -> str:
        return ',\n'.join(f'{event.beat}={event.value}' for event in self)


class EventTag(IntEnum):
    # When multiple events occur at the same time,
    # they should be processed in this order:
    AFTER_STOP = 0
    BPM = 1
    STOP = 2


@total_ordering
class TaggedBeatEvent(NamedTuple):
    event: BeatEvent
    tag: EventTag

    def __lt__(self, other):
        if self.event.beat < other.event.beat:
            return True
        if self.event.beat == other.event.beat:
            if self.tag < other.tag:
                return True
        return False


class SongTime(float):
    """
    A floating-point time value, denoting a temporal position / duration in a
    simfile.
    """
    def __repr__(self):
        return f'{self:.3f}'


class TimedEvent(NamedTuple):
    event: TaggedBeatEvent
    time: SongTime


class TimingData(NamedTuple):
    """
    Timing data for a simfile, possibly enriched with SSC chart timing.
    """
    bpms: BeatEvents
    stops: BeatEvents
    delays: BeatEvents
    warps: BeatEvents
    offset: Decimal

    @classmethod
    def from_simfile(
        cls: Type['TimingData'],
        simfile: Simfile,
        ssc_chart: SSCChart = SSCChart()
    ) -> 'TimingData':
        combined_properties = defaultdict(
            lambda: '',
            ChainMap(ssc_chart, simfile),
        )
        return TimingData(
            bpms=BeatEvents.from_str(combined_properties['BPMS']),
            stops=BeatEvents.from_str(combined_properties['STOPS']),
            delays=BeatEvents.from_str(combined_properties['DELAYS']),
            warps=BeatEvents.from_str(combined_properties['WARPS']),
            offset=Decimal(combined_properties['OFFSET']),
        )


class TimingConverter(object):
    """
    Utility class for converting song time to beats and vice-versa.

    Under the hood, this class arranges timing events chronologically,
    determines the song time and BPM at each event, then extrapolates
    from those calculated values for each :meth:`bpm_at` /
    :meth:`time_at` / :meth:`beat_at` call.
    """
    timing_data: TimingData
    bpms: BeatEvents
    stops: BeatEvents
    offset: Decimal
    timed_event_beats: MutableSequence[Beat]
    timed_event_times: MutableSequence[SongTime]
    timed_events: MutableSequence[TimedEvent]

    def __init__(self, timing_data: TimingData):
        self.timing_data = timing_data
        self._retime_events()
    
    def _retime_events(self):
        # Set the instance variables `timed_*` based on the simfile-backed
        # instance variables (bpms, stops, offset)
        first_bpm = self.timing_data.bpms[0]
        if first_bpm.beat != Beat(0):
            raise ValueError('first BPM change should be on beat 0')

        self.timed_events: MutableSequence[TimedEvent] = [
            TimedEvent(
                event=TaggedBeatEvent(event=first_bpm, tag=EventTag.BPM),
                time=-SongTime(self.timing_data.offset),
            ),
        ]

        all_events: Iterable[TaggedBeatEvent] = list(merge(*[
            list(map(
                lambda event: TaggedBeatEvent(event=event, tag=tag),
                events,
            )) for (events, tag) in [
                (self.timing_data.bpms[1:], EventTag.BPM),
                (self.timing_data.stops, EventTag.STOP),
            ]
        ]))
        
        current_bpm = first_bpm.value
        
        for tagged_event in all_events:
            event: BeatEvent = tagged_event.event
            tag: EventTag = tagged_event.tag
            
            previous_timed_event = self.timed_events[-1]
            beats_elapsed = event.beat - previous_timed_event.event.event.beat
            time_elapsed = beats_elapsed * 60 / float(current_bpm)
            new_time = previous_timed_event.time + time_elapsed
            
            self.timed_events.append(TimedEvent(
                event=tagged_event,
                time=SongTime(new_time),
            ))

            if tag == EventTag.BPM:
                current_bpm = event.value
            
            elif tag == EventTag.STOP:
                after_stop = Beat(event.beat + Beat.tick())
                time_elapsed = Beat.tick() * 60 / float(current_bpm) + float(event.value)
                new_time += time_elapsed
                self.timed_events.append(TimedEvent(
                    event=TaggedBeatEvent(
                        event=BeatEvent(beat=after_stop, value=Decimal(0)),
                        tag=EventTag.AFTER_STOP,
                    ),
                    time=SongTime(new_time),
                ))
        
        self.timed_event_beats = list(map(
            lambda timed_event: timed_event.event.event.beat,
            self.timed_events,
        ))

        self.timed_event_times = list(map(
            lambda timed_event: timed_event.time,
            self.timed_events,
        ))

    def bpm_at(self, beat: Beat) -> Decimal:
        """
        Determine the song's BPM at a given beat.
        """
        if beat < Beat(0):
            return Decimal(self.timing_data.bpms[0].value)
        
        previous_event_index = bisect(self.timed_event_beats, beat) - 1
        for i in range(previous_event_index, -1, -1):
            tagged_event: TaggedBeatEvent = self.timed_events[i].event
            if tagged_event.tag == EventTag.BPM:
                return tagged_event.event.value
        
        raise ValueError('first BPM change should be on beat 0')
    
    def time_at(self, beat: Beat) -> SongTime:
        """
        Determine the song time at a given beat.
        """
        # This variable name is a slight misnomer because if the provided beat
        # is negative, it will be clamped to index 0 (the initial BPM) which
        # comes after the beat. This works because the initial BPM applies to
        # negative beats and the signed math functions as expected.
        previous_event_index = max(0, bisect(self.timed_event_beats, beat) - 1)
        previous_event_beat = self.timed_event_beats[previous_event_index]
        previous_timed_event = self.timed_events[previous_event_index]
        
        beats_elapsed = beat - previous_event_beat
        time_elapsed = beats_elapsed * 60 / float(self.bpm_at(beat))

        return SongTime(previous_timed_event.time + time_elapsed)
    
    def beat_at(self, time: SongTime) -> Beat:
        """
        Determine the beat at a given time in the song.
        """
        # Same caveat as `time_at`
        previous_event_index = max(0, bisect(self.timed_event_times, time) - 1)
        previous_event_time = self.timed_event_times[previous_event_index]
        previous_timed_event = self.timed_events[previous_event_index]
        previous_event_beat = previous_timed_event.event.event.beat

        if previous_timed_event.event.tag == EventTag.STOP:
            return previous_event_beat
        
        time_elapsed = time - previous_event_time
        beats_elapsed = time_elapsed / 60 * float(self.bpm_at(previous_event_beat))

        return Beat(previous_event_beat + beats_elapsed).round_to_tick()