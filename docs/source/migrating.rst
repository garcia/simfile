.. _migrating:

Migrating from simfile 1.0 to 2.0
=================================

Version 1.0 of the :code:`simfile` library was released in 2013. It only
supported :code:`.sm` files and was primarily developed for Python 2, with
support for Python 3 on a separate branch.

Version 2.0 is a near-complete rewrite of the library, with :code:`.ssc`
support as the flagship feature. Aside from this and other features, the design
of the software has changed significantly to bring :code:`simfile` in line with
similar modern Python libraries.

Simfile & chart classes
-----------------------

In 1.0, the simfile & chart classes were :code:`simfile.Simfile` and
:code:`simfile.Chart`.

In 2.0, the simfile & chart classes are split by simfile type: for :code:`.sm`
files, the classes are :class:`simfile.sm.SMSimfile` and
:class:`simfile.sm.SMChart`, and for :code:`.ssc` files, the classes are
:class:`simfile.ssc.SSCSimfile` and :class:`simfile.ssc.SSCChart`.

Reading & writing simfiles
--------------------------

In 1.0, the :code:`Simfile` constructor accepted a filename or file object, and
a :code:`.from_string` class method handled loading from string data:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Robotix.sm')
    >>> # or...
    >>> with open('testdata/Robotix.sm', 'r') as infile:
    ...     sm = Simfile(infile)
    ...
    >>> # or...
    >>> sm = Simfile.from_string(str(sm))

In 2.0, each of these options has a corresponding function in the top-level
:mod:`simfile` module:

.. doctest::

    >>> import simfile # 2.0
    >>> sm = simfile.open('testdata/Robotix.sm')
    >>> # or...
    >>> with open('testdata/Robotix.sm', 'r') as infile:
    ...     sm = simfile.load(infile)
    ...
    >>> # or...
    >>> sm = simfile.loads(str(sm))

These methods determine which simfile format to use automatically, but you can
alternatively instantiate the simfile classes directly. They take a *named*
:code:`file` or :code:`string` argument:

.. doctest::

    >>> from simfile.sm import SMSimfile # 2.0
    >>> with open('testdata/Robotix.sm', 'r') as infile:
    ...     sm = SMSimfile(file=infile)
    ...
    >>> # or...
    >>> sm = SMSimfile(string=str(sm))

In 1.0, simfile objects had a :code:`.save` method that took a *maybe-optional*
filename parameter:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Robotix.sm') # filename supplied
    >>> sm.save() # writes to testdata/Robotix.sm
    >>> sm = Simfile.from_string(str(sm)) # no filename supplied
    >>> try:
    ...     sm.save() # to where?
    ... except ValueError:
    ...     sm.save('testdata/Robotix.sm') # much better 🙄

In 2.0, simfile objects no longer know their own filenames. Either pass a file
object to :meth:`simfile.base.BaseSimfile.serialize` or use
:func:`simfile.mutate` for a more guided workflow.

Simfile & chart data
--------------------

In 1.0, certain properties of simfiles and charts were automatically converted
from strings to richer representations.

*   The "BPMS" and "STOPS" simfile parameters were converted to :code:`Timing`
    objects that offered convenient access to the beat & value pairs:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Robotix.sm')
    >>> print(type(sm.bpms))
    <class 'simfile.simfile.Timing'>
    >>> print(type(sm.stops))
    <class 'simfile.simfile.Timing'>

*   The "meter" and "notes" chart attributes were converted to an integer and a
    :code:`Notes` object, respectively:

    >>> from simfile import Simfile # 1.0
    >>> sm = Simfile('testdata/Robotix.sm')
    >>> chart = sm.charts[0]
    >>> print(type(chart.meter))
    <class 'int'>
    >>> print(type(chart.notes))
    <class 'simfile.simfile.Notes'>

In 2.0, all properties of simfiles and charts are kept as strings. This
prevents wasting CPU cycles for use cases that don't benefit from the richer
representations, keeps the underlying data structures homogeneously typed, and
simplifies the serialization logic.

If you need rich timing data, use the :mod:`simfile.timing` module. If you need
rich note data, use the :mod:`simfile.notes` package and its submodules.
Keeping these modules separate from the core simfile & chart classes enables
them to be much more fully-featured than their 1.0 counterparts.