from bisect import bisect
from decimal import Decimal
from enum import IntEnum
from functools import total_ordering
from heapq import merge
from typing import Iterable, List, MutableSequence, Optional, Tuple, NamedTuple, cast

from . import Beat, BeatValue, BeatValues, TimingData
from simfile._private.generic import E, ListWithRepr
from simfile.types import Simfile


__all__ = [
    'SongTime', 'EventTag', 'TimingEngine', 
]


class SongTime(float):
    """
    A floating-point time value, denoting a temporal position in a simfile.
    """
    def __repr__(self):
        return f'{self:.3f}'


class EventTag(IntEnum):
    """
    Types of timing events.

    The order of these values determines how multiple events on the
    same beat will be sorted: for example, delays must occur before
    stops in order to correctly time notes on a beat with both a delay
    and a stop.

    Warps, delays, and stops have a corresponding "end" type that
    :class:`TimingEngine` uses to simplify the beat/time conversion
    logic. These types can be ignored as the results of passing them to
    :class:`TimingEngine`'s methods are never unique (i.e. you can get
    the same value by passing one of the other event types).
    """
    WARP = 0
    WARP_END = 1
    BPM = 2
    DELAY = 3
    DELAY_END = 4
    STOP = 5
    STOP_END = 6


@total_ordering
class TaggedEvent(NamedTuple):
    beat: Beat
    value: Decimal
    tag: EventTag

    def __lt__(self, other):
        if self.beat < other.beat:
            return True
        if self.beat == other.beat:
            if self.tag < other.tag:
                return True
        return False


class TimedEvent(NamedTuple):
    beat: Beat
    value: Decimal
    tag: EventTag
    time: SongTime


class TimingState(NamedTuple):
    event: TimedEvent
    bpm: Decimal
    warp: bool

    def time_until(self, beat: Beat, event_tag: EventTag) -> float:
        if self.warp:
            time_until = 0.0
        else:
            beats_until = beat - self.event.beat
            time_until = beats_until * 60 / float(self.bpm)
        
        if self.event.tag in (EventTag.STOP, EventTag.DELAY) \
            and event_tag in (EventTag.STOP_END, EventTag.DELAY_END):
            time_until += float(self.event.value)
        
        return time_until
    
    def beats_until(self, time: SongTime) -> Beat:
        if self.event.tag in (EventTag.STOP, EventTag.DELAY):
            return Beat(0)
        
        time_elapsed = time - self.event.time
        beats_elapsed = time_elapsed / 60 * float(self.bpm)

        return Beat(beats_elapsed).round_to_tick()


class TimingStateMachine(ListWithRepr[TimingState]):

    @property
    def last(self) -> TimingState:
        return cast(TimingState, self[-1])
    
    def advance(self, event: TaggedEvent):
        # Update song time
        time_until = self.last.time_until(event.beat, event.tag)
        time = SongTime(self.last.event.time + time_until)

        # Update BPM
        bpm = self.last.bpm
        if event.tag == EventTag.BPM:
            bpm = event.value
        
        # Update warp status
        warp = self.last.warp
        if event.tag == EventTag.WARP:
            warp = True
        elif event.tag == EventTag.WARP_END:
            warp = False
        
        self.append(TimingState(
            event=TimedEvent(
                beat=event.beat,
                value=event.value,
                tag=event.tag,
                time=time,
            ),
            bpm=bpm,
            warp=warp,
        ))


class TimingEngine:
    """
    Convert song time to beats and vice-versa.

    Under the hood, this class arranges timing events chronologically,
    determines the song time and BPM at each event, then extrapolates
    from those calculated values for each :meth:`bpm_at` /
    :meth:`time_at` / :meth:`beat_at` call.
    """
    timing_data: TimingData
    _tagged_beats: MutableSequence[Tuple[Beat, EventTag]]
    _tagged_times: MutableSequence[Tuple[SongTime, EventTag]]
    _state_machine: TimingStateMachine

    def __init__(self, timing_data: TimingData):
        self.timing_data = timing_data
        self._retime_events()
    
    def _coalesce_warps(self) -> Iterable[Tuple[BeatValues, EventTag]]:
        """
        Coalesce the timing data's warps into WARP & WARP_END events.

        StepMania allows warps to intersect. This is almost certainly
        unintended, but it means the most defensive option for this
        library is to handle intersecting warps the same way. This
        method keeps track of the warp state and ensures that the
        resulting sequences of events perfectly alternate between WARP
        and WARP_END events, combining any intersecting warps into
        singular warp segments.
        """
        zero = Decimal(0)
        warp_starts = BeatValues()
        warp_ends = BeatValues()
        for warp_ in self.timing_data.warps:
            warp: BeatValue = warp_
            warp_end = Beat(warp.beat + Beat(warp.value))
            if warp_starts:
                last_warp_end: Beat = warp_ends[-1].beat
                if warp.beat <= last_warp_end:
                    if warp_end > last_warp_end:
                        warp_ends[-1] = BeatValue(
                            beat=warp_end,
                            value=Decimal(0),
                        )
                else:
                    warp_starts.append(BeatValue(beat=warp.beat, value=zero))
                    warp_ends.append(BeatValue(beat=warp_end, value=zero))
            else:
                warp_starts.append(BeatValue(beat=warp.beat, value=zero))
                warp_ends.append(BeatValue(beat=warp_end, value=zero))
        
        return [
            (warp_starts, EventTag.WARP),
            (warp_ends, EventTag.WARP_END),
        ]

    
    def _retime_events(self):
        # Set the private instance variables based on the timing data
        first_bpm: BeatValue = self.timing_data.bpms[0]
        if first_bpm.beat != Beat(0):
            raise ValueError('first BPM change should be on beat 0')

        self._state_machine = TimingStateMachine([TimingState(
            event=TimedEvent(
                beat=Beat(0),
                value=first_bpm.value,
                tag=EventTag.BPM,
                time=-SongTime(self.timing_data.offset),
            ),
            bpm=first_bpm.value,
            warp=False,
        )])

        events_with_tags: Iterable[Tuple[BeatValues, EventTag]] = [
            *self._coalesce_warps(),
            (self.timing_data.bpms[1:], EventTag.BPM),
            (self.timing_data.delays, EventTag.DELAY),
            (self.timing_data.delays, EventTag.DELAY_END),
            (self.timing_data.stops, EventTag.STOP),
            (self.timing_data.stops, EventTag.STOP_END),
        ]

        chronological_events: Iterable[TaggedEvent] = merge(*[
            list(map(
                lambda e: TaggedEvent(beat=e.beat, value=e.value, tag=tag),
                events,
            )) for (events, tag) in events_with_tags
        ])
        
        for tagged_event in chronological_events:
            self._state_machine.advance(tagged_event)
        
        self._tagged_beats = list(map(
            lambda state: (state.event.beat, state.event.tag),
            cast(List[TimingState], self._state_machine),
        ))
        self._tagged_times = list(map(
            lambda state: (state.event.time, state.event.tag),
            cast(List[TimingState], self._state_machine),
        ))

    def bpm_at(self, beat: Beat) -> Decimal:
        """
        Determine the song's BPM at a given beat.
        """
        if beat < Beat(0):
            return Decimal(self.timing_data.bpms[0].value)
        
        tagged_beat = (beat, EventTag.BPM)
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
        tagged_beat = (beat, event_tag)
        
        # If the provided beat is negative, prior_state_index will be clamped
        # to index 0 (the initial BPM) which is not really the "prior state".
        # This works because the initial BPM applies to negative beats, and the
        # signed math works out correctly.
        prior_state_index = max(0, bisect(self._tagged_beats, tagged_beat) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]
        
        return SongTime(prior_state.event.time
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
        tagged_time = (time, event_tag)
        
        # Same caveat as `time_at`
        prior_state_index = max(0, bisect(self._tagged_times, tagged_time) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]
        prior_state_beat = prior_state.event.beat

        return Beat(prior_state_beat + prior_state.beats_until(time))
