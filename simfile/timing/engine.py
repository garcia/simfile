from bisect import bisect
from decimal import Decimal
from enum import IntEnum
from functools import total_ordering
from heapq import merge
from typing import Iterable, List, MutableSequence, Tuple, NamedTuple, Union, cast

from . import Beat, BeatValue, BeatValues, TimingData
from simfile._private.generic import ListWithRepr


__all__ = [
    "SongTime",
    "EventTag",
    "TimingEngine",
]


class SongTime(float):
    """
    A floating-point time value, denoting a temporal position in a simfile.
    """

    def __repr__(self) -> str:
        """
        Pretty repr() for song times.

        Includes the time to 3 decimal places.
        """
        return f"{self:.3f}"


SongTimeOrFloat = Union[SongTime, float]


class EventTag(IntEnum):
    """
    Types of timing events.

    The order of these values determines how multiple events on the
    same beat will be sorted: for example, delays must occur before
    stops in order to correctly time notes on a beat with both a delay
    and a stop.

    Warps, delays, stops, and fakes have a corresponding "end" type that
    :class:`TimingEngine` uses to simplify the beat/time conversion
    logic. These can be used to disambiguate the time at a given beat
    (for stops & delays) or the beat at a given time (for warps).
    """

    FAKE = -2
    FAKE_END = -1
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

    def __lt__(self, other) -> bool:
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
    fake: bool

    def time_until(self, beat: Beat, event_tag: EventTag) -> float:
        if self.warp:
            time_until = 0.0
        else:
            beats_until = beat - self.event.beat
            time_until = float(beats_until) * 60 / float(self.bpm)

        if self.event.tag in (EventTag.STOP, EventTag.DELAY) and event_tag in (
            EventTag.STOP_END,
            EventTag.DELAY_END,
        ):
            time_until += float(self.event.value)

        return time_until

    def beats_until(self, time: SongTimeOrFloat) -> Beat:
        if self.event.tag in (EventTag.STOP, EventTag.DELAY):
            return Beat(0)

        time_elapsed = time - self.event.time
        beats_elapsed = time_elapsed / 60 * float(self.bpm)

        return Beat(beats_elapsed)


class TimingStateMachine(ListWithRepr[TimingState]):
    @property
    def last(self) -> TimingState:
        return cast(TimingState, self[-1])

    def advance(self, event: TaggedEvent) -> None:
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

        # Update fake status
        fake = self.last.fake
        if event.tag == EventTag.FAKE:
            fake = True
        elif event.tag == EventTag.FAKE_END:
            fake = False

        self.append(
            TimingState(
                event=TimedEvent(
                    beat=event.beat,
                    value=event.value,
                    tag=event.tag,
                    time=time,
                ),
                bpm=bpm,
                warp=warp,
                fake=fake,
            )
        )


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
    _tagged_times: MutableSequence[Tuple[SongTime, Beat, EventTag]]
    _state_machine: TimingStateMachine

    def __init__(self, timing_data: TimingData):
        self.timing_data = timing_data
        self._retime_events()

    def _coalesce_fakes_and_warps(self) -> Iterable[Tuple[BeatValues, EventTag]]:
        """
        Coalesce the timing data's fakes and warps into
        FAKE, FAKE_END, WARP, and WARP_END events.

        StepMania allows fakes & warps to intersect. This is almost
        certainly unintended, but it means the most defensive option for
        this library is to handle intersecting warps the same way. This
        method keeps track of the fake & warp state and ensures that the
        resulting sequences of events perfectly alternate between start
        and end events, combining any intersections by eliding overshadowed
        end/start pairs.
        """
        zero = Decimal(0)

        def coalesce_event(beat_values) -> Tuple[BeatValues, BeatValues]:
            event_starts = BeatValues()
            event_ends = BeatValues()
            for event in beat_values:
                event_end = event.beat + Beat(event.value)
                if event_starts:
                    last_event_end: Beat = event_ends[-1].beat
                    if event.beat <= last_event_end:
                        if event_end > last_event_end:
                            event_ends[-1] = BeatValue(
                                beat=event_end,
                                value=zero,
                            )
                    else:
                        event_starts.append(BeatValue(beat=event.beat, value=zero))
                        event_ends.append(BeatValue(beat=event_end, value=zero))
                else:
                    event_starts.append(BeatValue(beat=event.beat, value=zero))
                    event_ends.append(BeatValue(beat=event_end, value=zero))

            return (event_starts, event_ends)

        fake_starts, fake_ends = coalesce_event(self.timing_data.fakes)
        warp_starts, warp_ends = coalesce_event(self.timing_data.warps)

        return [
            (fake_starts, EventTag.FAKE),
            (fake_ends, EventTag.FAKE_END),
            (warp_starts, EventTag.WARP),
            (warp_ends, EventTag.WARP_END),
        ]

    def _retime_events(self) -> None:
        # Set the private instance variables based on the timing data
        first_bpm: BeatValue = self.timing_data.bpms[0]
        if first_bpm.beat != 0:
            raise ValueError("first BPM change should be on beat 0")

        self._state_machine = TimingStateMachine(
            [
                TimingState(
                    event=TimedEvent(
                        beat=Beat(0),
                        value=first_bpm.value,
                        tag=EventTag.BPM,
                        time=SongTime(-self.timing_data.offset),
                    ),
                    bpm=first_bpm.value,
                    warp=False,
                    fake=False,
                )
            ]
        )

        events_with_tags: Iterable[Tuple[BeatValues, EventTag]] = [
            *self._coalesce_fakes_and_warps(),
            (cast(BeatValues, self.timing_data.bpms[1:]), EventTag.BPM),
            (self.timing_data.delays, EventTag.DELAY),
            (self.timing_data.delays, EventTag.DELAY_END),
            (self.timing_data.stops, EventTag.STOP),
            (self.timing_data.stops, EventTag.STOP_END),
        ]

        chronological_events: Iterable[TaggedEvent] = merge(
            *[
                list(
                    map(
                        lambda e: TaggedEvent(beat=e.beat, value=e.value, tag=tag),
                        events,
                    )
                )
                for (events, tag) in events_with_tags
            ]
        )

        for tagged_event in chronological_events:
            self._state_machine.advance(tagged_event)

        self._tagged_beats = list(
            map(
                lambda state: (state.event.beat, state.event.tag),
                self._state_machine,
            )
        )
        self._tagged_times = list(
            map(
                lambda state: (state.event.time, state.event.beat, state.event.tag),
                self._state_machine,
            )
        )

    def bpm_at(self, beat: Beat) -> Decimal:
        """
        Find the song's BPM at a given beat.

        Neither warps, stops, nor delays affect the output of this
        method: warps are not considered "infinite BPM", nor are pauses
        considered "zero BPM".
        """
        if beat < 0:
            return Decimal(self.timing_data.bpms[0].value)

        tagged_beat = (beat, EventTag.BPM)
        prior_state_index = max(0, bisect(self._tagged_beats, tagged_beat) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]
        return prior_state.bpm

    def hittable(self, beat: Beat) -> bool:
        """
        Determine if a note on the given beat would be hittable.

        A note is considered "unhittable" if and only if:

        * It takes place inside a warp segment (inclusive of the warp's
          start, exclusive of the warp's end).
        * It doesn't coincide with a stop or delay.

        StepMania internally converts unhittable notes to fake notes so
        that the player's score isn't affected by them.
        """
        tagged_beat = (beat, EventTag.STOP_END)
        prior_state_index = max(0, bisect(self._tagged_beats, tagged_beat) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]

        if prior_state.fake:
            return False

        if not prior_state.warp:
            return True

        if (
            prior_state.event.tag in (EventTag.STOP_END, EventTag.DELAY_END)
            and beat == prior_state.event.beat
        ):
            return True

        return False

    def time_at(self, beat: Beat, event_tag: EventTag = EventTag.STOP) -> SongTime:
        """
        Determine the song time at a given beat.

        On most beats, the `event_tag` parameter is inconsequential.
        The only time it matters is when stops or delays are involved:

        * On stops, providing a value of :data:`EventTag.STOP` or lower
          will return the time at which the stop is reached, whereas
          providing :data:`EventTag.STOP_END` will return the time when
          the stop ends.
        * On delays, providing a value of :data:`EventTag.DELAY` or
          lower will return the time at which the delay is reached,
          whereas providing :data:`EventTag.DELAY_END` or later will
          return the time when the delay ends.

        The default value of :data:`EventTag.STOP` effectively matches
        the time at which a note on the given beat must be hit
        (assuming such a note is :meth:`hittable`).
        """
        tagged_beat = (beat, event_tag)

        # If the provided beat is negative, prior_state_index will be clamped
        # to index 0 (the initial BPM) which is not really the "prior state".
        # This works because the initial BPM applies to negative beats, and the
        # signed math works out correctly.
        prior_state_index = max(0, bisect(self._tagged_beats, tagged_beat) - 1)
        prior_state: TimingState = self._state_machine[prior_state_index]

        return SongTime(
            prior_state.event.time + prior_state.time_until(beat, event_tag)
        )

    def beat_at(
        self,
        time: SongTimeOrFloat,
        event_tag: EventTag = EventTag.STOP,
    ) -> Beat:
        """
        Determine the beat at a given time in the song.

        At most times, the `event_tag` parameter is inconsequential.
        The only time it matters is when the time lands exactly on a
        warp segment:

        * Providing :data:`EventTag.WARP` will return the beat where
          the warp starts.
        * Providing :data:`EventTag.WARP_END` or later will return the
          beat where the warp ends (or is interrupted by a stop or
          delay).

        Keep in mind that this situation is floating-point precise, so
        it's unlikely for the `event_tag` to ever make a difference.
        """
        # Event tags can be out-of-order within a given instant of time,
        # so the beat must be stored before the event tag
        # to maintain natural ordering (and thus correct `bisect` behavior).
        # But this also means we cannot target an event tag within a time
        # directly through `bisect`, since we don't know the beat.
        tagged_time = (time, Beat(-1), EventTag.FAKE)
        bisect_index = bisect(self._tagged_times, tagged_time)

        if (
            bisect_index < len(self._state_machine)
            and self._state_machine[bisect_index].event.time == time
        ):
            # Hack: if multiple events happen at exactly the same time,
            # the only reason why the beat would be different across events
            # is when a warp ends at exactly that time. In this situation,
            # take the first event at that time given EventTag.WARP or earlier,
            # or the last event at that time given EventTag.WARP_END or later.
            prior_state_index = bisect_index
            if event_tag >= EventTag.WARP_END:
                while (
                    prior_state_index + 1 < len(self._state_machine)
                    and self._state_machine[prior_state_index + 1].event.time == time
                ):
                    prior_state_index += 1
        else:
            prior_state_index = max(0, bisect_index - 1)

        prior_state: TimingState = self._state_machine[prior_state_index]
        prior_state_beat = prior_state.event.beat

        return cast(Beat, prior_state_beat + prior_state.beats_until(time))
