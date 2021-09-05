.. _migrating:

Migrating from simfile 1.0 to 2.0
=================================

Version 1.0 of the **simfile** library was released in 2013. It only
supported SM files and was primarily developed for Python 2, with support for
Python 3 on a separate branch.

Version 2.0 is a near-complete rewrite of the library exclusively for Python 3,
with SSC support as the flagship feature. Aside from new features, the
design of the library has changed significantly to bring it in line with
similar modern Python libraries.

Simfile & chart classes
-----------------------

In 1.0, the simfile & chart classes were :code:`simfile.Simfile` and
:code:`simfile.Chart`.

In 2.0, the simfile & chart classes are split by simfile type:

* For SM files, the :mod:`simfile.sm` module provides :class:`.SMSimfile` and
  :class:`.SMChart`.
* For SSC files, the :mod:`simfile.ssc` module provides :class:`.SSCSimfile`
  and :class:`.SSCChart`.

Additionally, :mod:`simfile.types` provides the union types :data:`.Simfile`
and :data:`.Chart`, which are used to annotate parameters & return types where
either implementation is acceptable.

Reading simfiles
----------------

In 1.0, the :code:`Simfile` constructor accepted a filename or file object, and
a :code:`.from_string` class method handled loading from string data:

    >>> from simfile import Simfile # 1.0
    >>> from_filename = Simfile('testdata/Kryptix.sm')
    >>> # or...
    >>> with open('testdata/Kryptix.sm', 'r') as infile:
    ...     from_file_obj = Simfile(infile)
    ...
    >>> # or...
    >>> from_string = Simfile.from_string(str(from_file_obj))

In 2.0, each of these options has a corresponding function in the top-level
:mod:`simfile` module:

.. doctest::

    >>> import simfile # 2.0
    >>> from_filename = simfile.open('testdata/Kryptix.sm')
    >>> # or...
    >>> with open('testdata/Kryptix.sm', 'r') as infile:
    ...     from_file_obj = simfile.load(infile)
    ...
    >>> # or...
    >>> from_string = simfile.loads(str(from_file_obj))

These methods determine which simfile format to use automatically, but you can
alternatively instantiate the simfile classes directly. They take a *named*
:code:`file` or :code:`string` argument:

.. doctest::

    >>> from simfile.sm import SMSimfile # 2.0
    >>> with open('testdata/Kryptix.sm', 'r') as infile:
    ...     from_file_obj = SMSimfile(file=infile)
    ...
    >>> # or...
    >>> from_string = SMSimfile(string=str(from_file_obj))

Writing simfiles
----------------

In 1.0, simfile objects had a :code:`.save` method that took a *maybe-optional*
filename parameter:

    >>> from simfile import Simfile # 1.0
    >>> from_filename = Simfile('testdata/Kryptix.sm')        # filename supplied
    >>> from_filename.save()                                  # no problem!
    >>> from_string = Simfile.from_string(str(from_filename)) # no filename supplied
    >>> try:
    ...     from_string.save()                                # to where?
    ... except ValueError:
    ...     from_string.save('testdata/Kryptix.sm')           # much better 🙄

In 2.0, simfile objects no longer know their own filenames. Either pass a file
object to the simfile's :meth:`~simfile.base.BaseSimfile.serialize` method or
use :func:`simfile.mutate` for a more guided workflow.

Finding charts
--------------

In 1.0, the list of charts at :code:`Simfile.charts` offered convenience
methods for getting a single chart or finding multiple charts:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Kryptix.sm')
    >>> single_novice = sm.charts.get(difficulty='Beginner')
    >>> single_novice.stepstype
    dance-single
    >>> expert_charts = sm.charts.filter(difficulty='Challenge')
    >>> [ex.stepstype for ex in expert_charts]
    ['dance-double', 'dance-single']

In 2.0, these convenience methods have been removed in favor of for-loops and
the built-in :code:`filter` function. Writing your own predicates as Python
code is much more flexibile than the 1.0 convenience methods, which could only
find charts by exact property matches.

Special property types
----------------------

In 1.0, certain properties of simfiles and charts were automatically converted
from strings to richer representations.

*   The "BPMS" and "STOPS" simfile parameters were converted to :code:`Timing`
    objects that offered convenient access to the beat & value pairs:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Kryptix.sm')
    >>> print(type(sm['BPMS']))
    <class 'simfile.simfile.Timing'>
    >>> print(type(sm['STOPS']))
    <class 'simfile.simfile.Timing'>

*   The "meter" and "notes" chart attributes were converted to an integer and a
    :code:`Notes` object, respectively:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Kryptix.sm')
    >>> chart = sm.charts[0]
    >>> print(type(chart.meter))
    <class 'int'>
    >>> print(type(chart.notes))
    <class 'simfile.simfile.Notes'>

In 2.0, all properties of simfiles and charts are kept as strings. This
prevents wasting CPU cycles for use cases that don't benefit from the richer
representations, keeps the underlying data structures homogeneously typed, and
significantly reduces the number of reasons why parsing a simfile might fail.

If you need rich timing data, use the :mod:`simfile.timing` package:

    >>> import simfile # 2.0
    >>> from simfile.timing import TimingData
    >>> kryptix = simfile.open('testdata/Kryptix.sm')
    >>> timing_data = TimingData.from_simfile(kryptix)
    >>> print(timing_data.bpms[0])
    BeatValue(beat=Beat(0), value=Decimal('150.000'))

If you need rich note data, use the :mod:`simfile.notes` package:

    >>> import simfile # 2.0
    >>> from simfile.notes import NoteData
    >>> from simfile.timing import Beat
    >>> kryptix = simfile.open('testdata/Kryptix.sm')
    >>> for note in NoteData.from_chart(kryptix.charts[0]):
    ...     if note.beat > Beat(18): break
    ...     print(note)
    ...
    Note(beat=Beat(16.25), column=3, note_type=NoteType.TAP)
    Note(beat=Beat(16.5), column=2, note_type=NoteType.TAP)
    Note(beat=Beat(17.25), column=2, note_type=NoteType.TAP)
    Note(beat=Beat(17.5), column=3, note_type=NoteType.TAP)

Keeping these modules separate from the core simfile & chart classes enables
them to be much more fully-featured than their 1.0 counterparts.