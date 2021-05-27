.. _timing-note-data:

Timing & note data
==================

For advanced use cases that require parsing specific fields from simfiles and
charts, :code:`simfile` provides subpackages that interface with the core
simfile & chart classes. As of version 2.0, the available subpackages are
:mod:`simfile.notes` and :mod:`simfile.timing`.

Reading note data
-----------------

The primary function of a simfile is to store charts, and the primary function
of a chart is to store *note data* – sequences of inputs that the player must
follow to the rhythm of the song. Notes come in different types, appear in
different columns, and occur on different beats of the chart.

Rather than trying to parse a chart's :attr:`~.BaseChart.notes` field directly,
use the :class:`.NoteData` class:

.. doctest::

    >>> import simfile
    >>> from simfile.notes import NoteData
    >>> from simfile.timing import Beat
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> chart = springtime.charts[0]
    >>> note_data = NoteData.from_chart(chart)
    >>> note_data.columns
    4
    >>> for note in note_data:
    ...     if note.beat > Beat(18): break
    ...     print(note)
    ...
    Note(beat=<Beat 16>, column=2, note_type=<NoteType.TAP: '1'>)
    Note(beat=<Beat 16.5>, column=2, note_type=<NoteType.TAP: '1'>)
    Note(beat=<Beat 16.75>, column=0, note_type=<NoteType.TAP: '1'>)
    Note(beat=<Beat 17>, column=1, note_type=<NoteType.TAP: '1'>)
    Note(beat=<Beat 17.5>, column=0, note_type=<NoteType.TAP: '1'>)
    Note(beat=<Beat 17.75>, column=2, note_type=<NoteType.TAP: '1'>)
    Note(beat=<Beat 18>, column=1, note_type=<NoteType.TAP: '1'>)

There's no limit to how many notes a chart can contain – some have tens or even
hundreds of thousands! For this reason, :class:`.NoteData` only generates
:class:`.Note` objects when you ask for them, one at a time, rather than
storing a list of notes. Likewise, functions in this library that operate on
note data accept an iterator of notes, holding them in memory for as little
time as possible.

Counting notes
--------------

Counting notes isn't as straightforward as it sounds: there are different note
types and different ways to handle notes on the same beat. StepMania offers six
different "counts" on the music selection screen by default, each offering a
unique aggregation of the gameplay events in the chart.

You can use the :mod:`simfile.notes.count` module to reproduce all of these
counts:

.. doctest::

    >>> import simfile
    >>> from simfile.notes import NoteData
    >>> from simfile.notes.count import *
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> chart = springtime.charts[0]
    >>> note_data = NoteData.from_chart(chart)
    >>> count_steps(note_data)
    864
    >>> count_jumps(note_data)
    33

If the functions in this module aren't sufficient for your needs, move on to
the next section for more options.

Handling holds, rolls, and jumps
--------------------------------

Conceptually, **hold** and **roll** notes are atomic: while they have discrete
start and end beats, *both* endpoints must be specified for the note to be
valid. This logic also extends to **jumps** in certain situations: for example,
combo counters, judgement & score algorithms, and note counting methods may
consider jumps to be "equal" in some sense to isolated tap notes.

In contrast, iterating over :class:`.NoteData` yields a separate "note" for
every discrete event in the chart: hold and roll heads are separate from their
tails, and jumps are emitted one note at a time. You may want to group either
or both of these types of notes together, depending on your use case.

The :func:`.group_notes` function handles all of these cases. In this example,
we find that the longest hold in Springtime's Lv. 21 chart is 6½ beats long:

.. doctest::

    >>> import simfile
    >>> from simfile.notes import NoteType, NoteData
    >>> from simfile.notes.group import OrphanedNotes, group_notes
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> chart = next(filter(lambda chart: chart.meter == '21', springtime.charts))
    >>> note_data = NoteData.from_chart(chart)
    >>> group_iterator = group_notes(
    ...     note_data,
    ...     include_note_types={NoteType.HOLD_HEAD, NoteType.TAIL},
    ...     join_heads_to_tails=True,
    ...     orphaned_tail=OrphanedNotes.DROP_ORPHAN,
    ... )
    >>> longest_hold = 0
    >>> for grouped_notes in group_iterator:
    ...     note = note_group[0]
    ...     longest_hold = max(longest_hold, note.tail_beat - note.beat)
    ...
    >>> longest_hold
    Fraction(13, 2)

There's a lot going on in this code snippet, so here's a breakdown of the
important parts:

    >>> group_iterator = group_notes(
    ...     note_data,
    ...     include_note_types={NoteType.HOLD_HEAD, NoteType.TAIL},
    ...     orphaned_tail=OrphanedNotes.DROP_ORPHAN,
    ...     join_heads_to_tails=True,
    ... )

Here we choose to group hold heads to their tails, dropping any orphaned tails.
By default, orphaned heads or tails will raise an exception, but in this
example we've opted out of including roll heads, whose tails would become
orphaned. If we chose to include :attr:`.NoteType.ROLL_HEAD` in the set, then
we could safely omit the `orphaned_tail` argument since all tails should
have a matching head (assuming the chart is valid).

    >>> for grouped_notes in group_iterator:
    ...     note = note_group[0]
    ...     longest_hold = max(longest_hold, note.tail_beat - note.beat)

The :func:`.group_notes` function yields *lists of notes* rather than single
notes. In this example, every list will only have a single element because we
haven't opted into joining notes that occur on the same beat (we would do so
using the `same_beat_notes` parameter). As such, we can extract the single note
by indexing into each note group.

You'll notice that we're using a :attr:`~.NoteWithTail.tail_beat` attribute,
which isn't present in the :class:`.Note` class. That's because these notes are
actually :class:`.NoteWithTail` instances: the *lists of notes* referenced
above are actually lists of :class:`.Note` and/or :class:`.NoteWithTail`
objects, depending on the parameters. In this case, we know that *every* note
will be a :class:`.NoteWithTail` instance because we've only included head and
tail note types, which will be joined together.

Out of all the possible combinations of :func:`.group_notes` parameters, this
example yields fairly simple items (singleton lists of :class:`.NoteWithTail`
instances). Other combinations of parameters may yield variable-length lists
where you need to explicitly check the type of the elements.

Reading timing data
-------------------

Rather than reading fields like :code:`BPMS` and :code:`STOPS` directly from
the simfile, use the :class:`.TimingData` class:

.. doctest::

    >>> import simfile
    >>> from simfile.timing import TimingData
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> timing_data = TimingData.from_simfile(springtime)
    >>> timing_data.bpms
    BeatValues([BeatValue(beat=<Beat 0>, value=Decimal('181.685'))])

The SSC format introduces "split timing" – per-chart timing data – which
:class:`.TimingData` empowers you to handle as effortlessly as providing the
chart:

.. doctest::

    >>> import simfile
    >>> from simfile.timing import TimingData
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> chart = springtime.charts[0]
    >>> split_timing = TimingData.from_simfile(springtime, chart)
    >>> split_timing.bpms
    BeatValues([BeatValue(beat=<Beat 0>, value=Decimal('181.685')), BeatValue(beat=<Beat 304>, value=Decimal('90.843')), BeatValue(beat=<Beat 311>, value=Decimal('181.685'))])

This works regardless of whether the chart has split timing, or even whether
the simfile is an SSC file; if the chart has no timing data of its own, it will
be ignored and the simfile's timing data will be used instead.

Getting the displayed BPM
-------------------------

On StepMania's music selection screen, players can typically see the selected
chart's BPM range - either a static value, a range of values, or an animation
of random values (sometimes used to make "boss songs" look more intimidating).

To get the displayed BPM, use the :func:`.displaybpm` function:

.. doctest::

    >>> import simfile
    >>> from simfile.timing.displaybpm import displaybpm
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> displaybpm(springtime)
    StaticDisplayBPM(value=Decimal('182'))

The return value will be one of :class:`.StaticDisplayBPM`,
:class:`.RangeDisplayBPM`, or :class:`.RandomDisplayBPM`. These classes offer
different methods for fetching the BPM value(s), so if you're working with
arbitrary simfiles, you'll want to handle each case separately using
:code:`instanceof()` checks.

Much like :class:`.TimingData`, :func:`.displaybpm` accepts an optional chart
parameter for SSC split timing.

Converting song time to beats
-----------------------------

If you wanted to implement a simfile editor or gameplay engine, you'd need some
way to convert song time to beats and vice-versa. To reach feature parity with
StepMania, you'd need to implement BPM changes, stops, delays, and warps in
order for your application to support all the simfiles that StepMania accepts.

Consider using the :class:`.TimingEngine` for this use case:

.. doctest::

    >>> import simfile
    >>> from simfile.timing import Beat, TimingData
    >>> from simfile.timing.engine import TimingEngine
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> timing_data = TimingData.from_simfile(springtime)
    >>> engine = TimingEngine(timing_data)
    >>> engine.time_at(Beat(32))
    10.658
    >>> engine.beat_at(10.658)
    <Beat 32>

This engine handles all of the timing events described above, including edge
cases involving overlapping stops, delays, and warps. You can even check
whether a note near a warp segment would be :meth:`.hittable` or not!

Combining notes and time
------------------------

Finally, to tie everything together, check out the :func:`.time_notes` function
which converts a :class:`.Note` stream into a :class:`.TimedNote` stream:

.. doctest::

    >>> import simfile
    >>> from simfile.timing import Beat, TimingData
    >>> from simfile.notes import NoteData
    >>> from simfile.notes.timed import time_notes
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> chart = springtime.charts[0]
    >>> note_data = NoteData.from_chart(chart)
    >>> timing_data = TimingData.from_simfile(springtime, chart)
    >>> for timed_note in time_notes(note_data, timing_data):
    ...     if 60 < timed_note.time < 61:
    ...         print(timed_note)
    ...
    TimedNote(time=60.029, note=Note(beat=<Beat 181.5>, column=3, note_type=<NoteType.TAP: '1'>))
    TimedNote(time=60.194, note=Note(beat=<Beat 182>, column=0, note_type=<NoteType.HOLD_HEAD: '2'>))
    TimedNote(time=60.524, note=Note(beat=<Beat 183>, column=3, note_type=<NoteType.TAP: '1'>))
    TimedNote(time=60.855, note=Note(beat=<Beat 184>, column=2, note_type=<NoteType.TAP: '1'>))

You could use this to determine the notes per second (NPS) over the entire
chart, or at a specific time like the example above. Get creative!