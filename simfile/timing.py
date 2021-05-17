from bisect import bisect, insort
from collections import ChainMap, defaultdict
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction
from functools import total_ordering
from heapq import merge
from simfile.ssc import SSCChart
from typing import Iterable, MutableSequence, Optional, Tuple, Type, NamedTuple, Union, cast

from ._private.generic import E, ListWithRepr
from .types import Simfile


__all__ = [
    'Beat', 'BeatEvent', 'BeatEvents', 'SongTime', 'TimingData',
    'TimingConverter', 'StaticDisplayBPM', 'RangeDisplayBPM',
    'RandomDisplayBPM', 'DisplayBPM', 'displaybpm',
]


MEASURE_SUBDIVISION = 192
BEAT_SUBDIVISION = MEASURE_SUBDIVISION // 4


class Beat(Fraction):
    """
    A fractional beat value, denoting vertical position in a simfile.
    """

    @classmethod
    def tick(cls) -> 'Beat':
        """
        1/48 of a beat (1/192 of a measure).
        """
        return cls(1, BEAT_SUBDIVISION)
    
    @classmethod
    def from_str(cls, beat_str) -> 'Beat':
        """
        Convert a decimal string to a beat, rounding to the nearest tick.
        """
        return Beat(beat_str).round_to_tick()
    
    def round_to_tick(self) -> 'Beat':
        """
        Round the beat to the nearest tick.
        """
        return Beat(int(round(self * BEAT_SUBDIVISION)), BEAT_SUBDIVISION)
    
    def __str__(self):
        """
        Convert the beat to a string with 3 decimal digits.
        """
        return f'{float(self):.3f}'
    
    def __repr__(self):
        """
        Pretty repr() for beats.

        Includes the string representation with at most 3 decimal
        digits, with trailing zeros removed.
        """
        return f"<Beat {str(self).rstrip('0').rstrip('.')}>"


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
        """
        Parse the MSD value component of a timing data list.

        Specifically, `BPMS`, `STOPS`, `DELAYS`, and `WARPS` are
        the timing data lists whose values can be parsed by this
        method.
        """
        instance = cls()
        
        if string.strip():
            for row in string.split(','):
                beat, value = row.strip().split('=')
                instance.append(BeatEvent(Beat.from_str(beat), Decimal(value)))
        
        return instance

    def serialize(self) -> str:
        return ',\n'.join(f'{event.beat}={event.value}' for event in self)


def _ssc_proxy(simfile: Simfile, ssc_chart: SSCChart):
    return defaultdict(lambda: '', ChainMap(ssc_chart, simfile))


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
        """
        Obtain timing data from a simfile and optionally an SSC chart.

        If an SSC chart is provided, any timing data properties it
        contains will take precedence over the simfile's timing data.
        This is true regardless of the property's value; for example, a
        blank `STOPS` value in the SSC chart overrides a non-blank
        value from the simfile.
        """
        properties = _ssc_proxy(simfile, ssc_chart)
        return TimingData(
            bpms=BeatEvents.from_str(properties['BPMS']),
            stops=BeatEvents.from_str(properties['STOPS']),
            delays=BeatEvents.from_str(properties['DELAYS']),
            warps=BeatEvents.from_str(properties['WARPS']),
            offset=Decimal(properties['OFFSET']),
        )


class SongTime(float):
    """
    A floating-point time value, denoting a temporal position in a simfile.
    """
    def __repr__(self):
        return f'{self:.3f}'


class EventTag(IntEnum):
    # When multiple events occur at the same time,
    # they should be processed in this order:
    WARP = 0
    WARP_END = 1
    BPM = 2
    DELAY = 3
    DELAY_END = 4
    STOP = 5
    STOP_END = 6


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


class TimedEvent(NamedTuple):
    event: TaggedBeatEvent
    time: SongTime


class TimingState(NamedTuple):
    timed_event: TimedEvent
    bpm: Decimal
    warp_until: Optional[Beat]

    def time_until(self, beat: Beat, event_tag: EventTag) -> float:
        beat_event = self.timed_event.event.event

        if self.warp_until:
            assert beat <= self.warp_until
            time_until = 0.0
        else:
            beats_until = beat - beat_event.beat
            time_until = beats_until * 60 / float(self.bpm)
        
        if self.timed_event.event.tag in (EventTag.STOP, EventTag.DELAY) \
            and event_tag in (EventTag.STOP_END, EventTag.DELAY_END):
            time_until += float(beat_event.value)
        
        return time_until
    
    def beats_until(self, time: SongTime) -> Beat:
        beat_event = self.timed_event.event.event
        if self.timed_event.event.tag in (EventTag.STOP, EventTag.DELAY):
            return Beat(0)
        
        time_elapsed = time - self.timed_event.time
        beats_elapsed = time_elapsed / 60 * float(self.bpm)

        return Beat(beats_elapsed).round_to_tick()


class TimingStateMachine(ListWithRepr[TimingState]):

    @property
    def last(self) -> TimingState:
        return cast(TimingState, self[-1])
    
    def advance(self, tagged_event: TaggedBeatEvent):
        beat_event = tagged_event.event

        # Insert WARP_END event if we're currently inside a warp and EITHER
        # 1. advancing past the warp end OR
        # 2. arriving at the warp end without immediately entering another warp
        if (tagged_event.tag != EventTag.WARP_END
            and self.last.warp_until
            and (beat_event.beat > self.last.warp_until
                or (beat_event.beat == self.last.warp_until
                    and tagged_event.tag != EventTag.WARP))):
            self.advance(TaggedBeatEvent(
                event=BeatEvent(beat=self.last.warp_until, value=Decimal(0)),
                tag=EventTag.WARP_END,
            ))
        
        # Update song time
        time_until = self.last.time_until(beat_event.beat, tagged_event.tag)
        time = SongTime(self.last.timed_event.time + time_until)

        # Update BPM
        bpm = self.last.bpm
        if tagged_event.tag == EventTag.BPM:
            bpm = beat_event.value
        
        # Update warp status
        warp_until = self.last.warp_until
        if tagged_event.tag == EventTag.WARP_END:
            warp_until = None
        elif tagged_event.tag == EventTag.WARP:
            warp_end = Beat(beat_event.beat + Beat(beat_event.value))
            if warp_until is None or warp_end > warp_until:
                warp_until = warp_end
        
        # Make sure we didn't somehow go past the warp end
        if warp_until:
            assert beat_event.beat < warp_until
        
        self.append(TimingState(
            timed_event=TimedEvent(event=tagged_event, time=time),
            bpm=bpm,
            warp_until=warp_until,
        ))


@total_ordering
class TaggedBeat(NamedTuple):
    beat: Beat
    tag: EventTag

    @classmethod
    def from_timing_state(cls, state: TimingState) -> 'TaggedBeat':
        return TaggedBeat(
            beat=state.timed_event.event.event.beat,
            tag=state.timed_event.event.tag,
        )

    def __lt__(self, other):
        if self.beat < other.beat:
            return True
        if self.beat == other.beat:
            if self.tag < other.tag:
                return True
        return False


@total_ordering
class TaggedSongTime(NamedTuple):
    time: SongTime
    tag: EventTag

    @classmethod
    def from_timing_state(cls, state: TimingState) -> 'TaggedSongTime':
        return TaggedSongTime(
            time=state.timed_event.time,
            tag=state.timed_event.event.tag,
        )

    def __lt__(self, other):
        if self.time < other.time:
            return True
        if self.time == other.time:
            if self.tag < other.tag:
                return True
        return False


class TimingConverter:
    """
    Utility class for converting song time to beats and vice-versa.

    Under the hood, this class arranges timing events chronologically,
    determines the song time and BPM at each event, then extrapolates
    from those calculated values for each :meth:`bpm_at` /
    :meth:`time_at` / :meth:`beat_at` call.
    """
    timing_data: TimingData
    _tagged_beats: MutableSequence[TaggedBeat]
    _tagged_times: MutableSequence[TaggedSongTime]
    _state_machine: TimingStateMachine

    def __init__(self, timing_data: TimingData):
        self.timing_data = timing_data
        self._retime_events()
    
    def _retime_events(self):
        # Set the private instance variables based on the timing data
        first_bpm: BeatEvent = self.timing_data.bpms[0]
        if first_bpm.beat != Beat(0):
            raise ValueError('first BPM change should be on beat 0')

        self._state_machine = TimingStateMachine([TimingState(
            timed_event=TimedEvent(
                event=TaggedBeatEvent(event=first_bpm, tag=EventTag.BPM),
                time=-SongTime(self.timing_data.offset),
            ),
            bpm=first_bpm.value,
            warp_until=None,
        )])

        all_events: Iterable[TaggedBeatEvent] = merge(*[
            list(map(
                lambda event: TaggedBeatEvent(event=event, tag=tag),
                events,
            )) for (events, tag) in [
                (self.timing_data.warps, EventTag.WARP),
                (self.timing_data.bpms[1:], EventTag.BPM),
                (self.timing_data.delays, EventTag.DELAY),
                (self.timing_data.delays, EventTag.DELAY_END),
                (self.timing_data.stops, EventTag.STOP),
                (self.timing_data.stops, EventTag.STOP_END),
            ]
        ])
        
        for tagged_event in all_events:
            self._state_machine.advance(tagged_event)
        
        self._tagged_beats = list(map(
            TaggedBeat.from_timing_state,
            self._state_machine,
        ))
        self._tagged_times = list(map(
            TaggedSongTime.from_timing_state,
            self._state_machine,
        ))

    def bpm_at(self, beat: Beat) -> Decimal:
        """
        Determine the song's BPM at a given beat.
        """
        if beat < Beat(0):
            return Decimal(self.timing_data.bpms[0].value)
        
        tagged_beat = TaggedBeat(beat=beat, tag=EventTag.BPM)
        prior_state_index = max(0, bisect(self._tagged_beats, tagged_beat) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]
        return prior_state.bpm
    
    def time_range(self, beat: Beat) -> Tuple[SongTime, SongTime]:
        """
        Determine when a given beat visibly overlaps the receptors.

        Most beats map to exactly one time, so both values of the range
        will be the same (and equal to :meth:`time_at`). The one
        exception is when stops or delays are involved: the range of
        song times will cover the duration of the pause. The first
        value is always less than or equal to the second value.

        During warps, this method returns the time at which the
        enclosing warp occurs for both values.
        """
        raise NotImplementedError

    def time_at(
        self,
        beat: Beat,
        event_tag: EventTag = EventTag.STOP
    ) -> Optional[SongTime]:
        """
        Determine the time at which a note on the given beat must be hit.

        Most beats map to exactly one time, so this value will be equal
        to both values returned by :meth:`time_range`. However, on
        stops and delays, this value will instead fall somewhere within
        the :meth:`time_range`:

        * On stops, this value is equal to the range's lower bound.
        * On delays, this value is equal to the range's upper bound.
        * On beats with both a stop and delay, this value is equal to
          the lower bound plus the length of the delay (or,
          equivalently, the upper bound minus the length of the stop).

        If a note placed at the given beat would be un-hittable due to
        a warp, this method will return None.
        """
        tagged_beat = TaggedBeat(beat=beat, tag=event_tag)
        
        # If the provided beat is negative, prior_state_index will be clamped
        # to index 0 (the initial BPM) which is not really the "prior state".
        # This works because the initial BPM applies to negative beats, and the
        # signed math works out correctly.
        prior_state_index = max(0, bisect(self._tagged_beats, tagged_beat) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]
        
        return SongTime(prior_state.timed_event.time
            + prior_state.time_until(beat, event_tag))
    
    def beat_at(
        self,
        time: SongTime,
        event_tag: EventTag = EventTag.STOP
    ) -> Beat:
        """
        Determine the beat at a given time in the song.

        No special provisions are made to handle warps; a song time
        that happens to land exactly on a warp might get mapped to the
        beat at which the warp starts or ends, depending on floating
        point rounding.
        """
        tagged_time = TaggedSongTime(time=time, tag=event_tag)
        
        # Same caveat as `time_at`
        prior_state_index = max(0, bisect(self._tagged_times, tagged_time) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]
        prior_state_beat = prior_state.timed_event.event.event.beat

        return Beat(prior_state_beat + prior_state.beats_until(time))


class StaticDisplayBPM(NamedTuple):
    """A single BPM value."""
    value: Decimal

    @property
    def min(self) -> Decimal:
        """Returns the single BPM value."""
        return self.value

    @property
    def max(self) -> Decimal:
        """Returns the single BPM value."""
        return self.value


class RangeDisplayBPM(NamedTuple):
    """A range of BPM values."""
    min: Decimal
    max: Decimal


class RandomDisplayBPM:
    """
    Used by StepMania to obfuscate the displayed BPM with random numbers.
    """


DisplayBPM = Union[StaticDisplayBPM, RangeDisplayBPM, RandomDisplayBPM]
"""Union of the three DisplayBPM variants above."""


def displaybpm(
    simfile: Simfile,
    ssc_chart: SSCChart = SSCChart()
) -> DisplayBPM:
    """
    Get the display BPM from a simfile and optionally an SSC chart.

    If a DISPLAYBPM property is present, its value is used as follows:

    * One number maps to :class:`StaticDisplayBPM`
    * Two ":"-separated numbers maps to :class:`RangeDisplayBPM`
    * A literal "*" maps to :class:`RandomDisplayBPM`

    Otherwise, the BPMS property will be used. A single BPM maps to
    :class:`StaticDisplayBPM`; if there are multiple, the minimum and
    maximum will be identified and passed to :class:`RangeDisplayBPM`.

    When an SSC chart is provided, its properties override those in the
    simfile.
    """
    properties = _ssc_proxy(simfile, ssc_chart)
    if 'DISPLAYBPM' in properties:
        displaybpm_value = properties['DISPLAYBPM']
        if displaybpm_value == '*':
            return RandomDisplayBPM()
        elif ':' in displaybpm_value:
            min, _, max = displaybpm_value.partition(':')
            return RangeDisplayBPM(min=Decimal(min), max=Decimal(max))
        else:
            return StaticDisplayBPM(value=Decimal(displaybpm_value))
    else:
        bpms = [e.value for e in BeatEvents.from_str(properties['BPMS'])]
        if len(bpms) == 1:
            return StaticDisplayBPM(bpms[0])
        else:
            return RangeDisplayBPM(min=min(bpms), max=max(bpms))
