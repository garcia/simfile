.. _timing:

Timing data
===========

**Timing data** is the properties of a simfile
that determine when notes must be hit.
For simple songs,
this typically just means two things:
an initial BPM
and an offset to synchronize the audio file to the steps.
However,
simfile authors have many more options to control the exact timing,
including:

* BPM changes
* Stops or delays (pausing the scrolling notes)
* Fakes (segments where all notes are considered fake & thus unhittable)
* Warps (segments that are instantly skipped over, rendering any warped-over notes fake)

The SM format only supports BPM changes, stops, and delays -
and only at the simfile level.
The newer SSC format introduces fakes and warps;
it also supports *split timing*, where a chart has its own timing data
that overrides the simfile timing data.

Working with timing data
------------------------

Import :class:`simfile.timing.TimingData`
and pass it a :data:`.Simfile` or an :data:`.AttachedChart`
to parse its timing data:

.. code:: python

    >>> import simfile
    >>> from simfile.timing import TimingData
    >>>
    >>> sim = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> timing_data = TimingData(sim)

.. note::

    You can *always* pass an :data:`.AttachedChart`,
    even if it's an :class:`.SMChart`!
    If the chart has no timing data of its own,
    :class:`.TimingData` will use the simfile's timing properties instead.

Read the parsed timing data using attributes with the same names as in the simfile:

.. code:: python

    >>> timing_data.offset
    Decimal('-0.090')
    >>> timing_data.bpms
    BeatValues([BeatValue(beat=Beat(0), value=Decimal('181.685'))])
    >>> timing_data.stops
    BeatValues([])

``Decimal`` is the built-in Python `Decimal class <https://docs.python.org/3/library/decimal.html>`_.
:class:`.BeatValues` is a thin subclass of Python's ``list``
that contains :class:`.BeatValue` objects.

:class:`.TimingData` is a mutable data structure,
much like :data:`.Simfile` & :data:`.Chart` objects.
However, changes made to :class:`.TimingData` do *not* automatically propagate
back to the :data:`.Simfile` or :data:`.Chart` they came from.
Use :meth:`.TimingData.write_to` to update the source object:

.. code:: python

    >>> import decimal
    >>> timing_data.offset += Decimal('0.009')
    >>> timing_data.write_to(sim)
    >>> sim.offset
    '-0.081'

Converting between beats and time
---------------------------------

Import :class:`~.TimingEngine` and pass it a :class:`.TimingData` object
to convert between beats and time:

.. code:: python

    >>> import simfile
    >>> from simfile.timing import TimingData
    >>> from simfile.timing.engine import TimingEngine
    >>>
    >>> sim = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> timing_data = TimingData(sim)
    >>> timing_engine = TimingEngine(timing_data)
    >>> timing_engine.time_at(Beat(32))
    10.658
    >>> timing_engine.beat_at(10.658)
    Beat(32)

Because :class:`.TimingData` stores fake regions and warps,
you can also use it to determine whether a regular note on a given beat would be hittable:

.. code:: python

    >>> timing_engine.hittable(Beat(32))
    True

However, this doesn't account for the fake *note type* (``F`` in note data).
So, you may prefer to import the :func:`~.time_chart` function
and pass it an :data:`.AttachedChart`.
This function yields :class:`.TimedNote` objects
that have :attr:`~.TimedNote.time` and :attr:`~.TimedNote.hittable` fields,
the latter of which is set to ``False`` for both region-based and single-note fakes:

.. code:: python

    >>> import simfile
    >>> from simfile.notes.timed import time_chart
    >>> 
    >>> sim = simfile.open('testdata/spin_cycle/spin_cycle.ssc')
    >>> for timed_note in time_chart(sim.charts[0]):
    ...     if not timed_note.hittable:
    ...         print(f"First fake note on beat {timed_note.note.beat} / time {timed_note.time}")
    ...         break
    ...
    First fake note on beat 327.000 / time 130.791
    >>>

Display BPM
-----------

Simfiles have an optional :attr:`~.BaseSimfile.displaybpm` attribute
that determines how to display the song's BPM on the music selection screen.
It can be a single BPM, a ``:``-separated BPM range,
or an asterisk ``*`` to hide the BPM from the player.
If there's no :attr:`~.BaseSimfile.displaybpm` set,
StepMania uses the actual :attr:`~.BaseSimfile.bpms` to determine what to display instead.

Import the :func:`~.displaybpm.displaybpm` function and
pass it a :data:`.Simfile` or an :data:`.AttachedChart`
to get the displayed BPM as an object:

.. code:: python

    >>> import simfile
    >>> from simfile.timing.displaybpm import displaybpm
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> disp = displaybpm(springtime)
    >>> if disp.value:
    ...     print(f"Static value: {disp.value}")
    ... elif disp.range:
    ...     print(f"Range of values: {disp.range[0]}-{disp.range[1]}")
    ... else:
    ...     print(f"* (obfuscated BPM)")
    ...
    Static value: 182

The return value will be one of
:class:`.StaticDisplayBPM`, :class:`.RangeDisplayBPM`, or :class:`.RandomDisplayBPM`.
All of these classes implement the same four properties,
so you typically don't need to check which class you got.
Here are some example inputs & outputs:

========== ================== ========================= ==== ==== ===== ==========
Actual BPM `DISPLAYBPM` value Class                     min  max  value range
========== ================== ========================= ==== ==== ===== ==========
300                           :class:`StaticDisplayBPM` 300  300  300   None
12-300     :code:`300`        :class:`StaticDisplayBPM` 300  300  300   None
12-300                        :class:`RangeDisplayBPM`  12   300  None  (12, 300)
12-300     :code:`150:300`    :class:`RangeDisplayBPM`  150  300  None  (150, 300)
12-300     :code:`*`          :class:`RandomDisplayBPM` None None None  None
========== ================== ========================= ==== ==== ===== ==========

If you want to ignore the `DISPLAYBPM` and get the actual BPM value / range,
pass ``ignore_specified=True`` to the :func:`.displaybpm` function:

.. code:: python

    disp = displaybpm(sf)
    if not disp.max:  # This means we got a RandomDisplayBPM
        disp = displaybpm(sf, ignore_specified=True)

.. warning::

    If you're familiar with how M-Mods work,
    it may seem intuitive that you could calculate the scroll rate
    based on the :attr:`~.RangeDisplayBPM.max` displayed BPM.
    However, be warned that StepMania ignores BPMs above some threshold,
    and that threshold is set by the active StepMania theme
    (and so is effectively arbitrary).
    A maximum BPM above 500 or so
    should be considered untrustworthy for M-Mod calculations
    due to this quirk of StepMania.
