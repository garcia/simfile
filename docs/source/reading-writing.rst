Reading & writing simfiles
==========================

Reading simfiles from disk
--------------------------

The top-level :mod:`simfile` module offers convenience functions for loading
simfiles from the filesystem.

Use :py:func:`simfile.open` to load a simfile by filename:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> print(springtime)
    <SSCSimfile: Springtime>
    >>> print(springtime.artist)
    Kommisar

Alternatively, if you have your own file object or string containing simfile
data, use :func:`simfile.load` or :func:`simfile.loads`:

.. doctest::

    >>> import simfile
    >>> with open('testdata/Springtime.ssc', 'r') as infile:
    ...     springtime = simfile.load(infile)
    ...
    >>> string_contents = str(springtime)
    >>> springtime2 = simfile.loads(string_contents)
    >>> springtime == springtime2
    True

Notice that :code:`str(simfile)` turns the simfile object back into the raw
file contents.

The type returned by these functions is declared as
:data:`simfile.types.Simfile`. This is a union of the two actual simfile types,
:class:`simfile.sm.SMSimfile` and :class:`simfile.ssc.SSCSimfile`:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> type(springtime)
    <class 'simfile.ssc.SSCSimfile'>
    >>> robotix = simfile.open('testdata/Robotix.sm')
    >>> type(robotix)
    <class 'simfile.sm.SMSimfile'>

The "magic" that determines which type to use is documented under
:func:`simfile.load`. If you'd rather use the underlying types directly,
instantiate them with either a `file` or `string` argument:

.. doctest::

    >>> from simfile.ssc import SSCSimfile
    >>> with open('testdata/Springtime.ssc', 'r') as infile:
    ...     springtime = SSCSimfile(file=infile)

Note that the underlying simfile types don't know about the filesystem: you
can't pass them a filename directly, nor do they offer a `.save()` method. This
is different from how version 1.0 of this package worked; refer to
:ref:`migrating` for more details on the differences.

Accessing simfile properties
----------------------------

Earlier we used the :attr:`~.BaseSimfile.title` attribute to get a simfile's
title, but we could have used a key lookup as well:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> springtime.title == springtime['TITLE']
    True

Both simfile formats have a predefined set of "known properties" - properties
used by StepMania and/or written by the StepMania editor - which can be
accessed as attributes. The known properties for SSC files are a *superset* of
those for SM files; the properties they have in common can be found in the
:mod:`simfile.base` documentation, and the ones added by the SSC format are
documented under :mod:`simfile.ssc`.

If a property isn't "known", it can still be accessed through the dict-like
interface. In fact, simfile objects extend :code:`OrderedDict`, so you can
access & manipulate their properties as a dictionary of uppercase string keys
mapped to string values:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> for property, value in springtime.items():
    ...     if property == 'TITLETRANSLIT': break
    ...     print(property, '=', repr(value))
    ...
    VERSION = '0.83'
    TITLE = 'Springtime'
    SUBTITLE = ''
    ARTIST = 'Kommisar'

.. note::

    One consequence of the backing :code:`OrderedDict` is that **duplicate
    properties are not preserved.** This is a rare occurrence among existing
    simfiles, usually indicative of manual editing, and it doesn't appear to
    have any practical use case. However, if the loss of this information is a
    concern, consider using
    `msdparser <https://msdparser.readthedocs.io/en/latest/>`_ to stream the
    key-value pairs directly.

Accessing charts
----------------

Stepcharts don't fit the key-value pattern used to store simfile properties, so
they are stored in a list under the :attr:`~.BaseSimfile.charts` attribute:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> len(springtime.charts)
    9
    >>> springtime.charts[0]
    <SSCChart: dance-single Challenge 12>

To find a particular chart, use a for-loop or Python's built-in :code:`filter`
function:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> list(filter(
    ...     lambda chart: chart.stepstype == 'pump-single' and int(chart.meter) > 20,
    ...     springtime.charts,
    ... ))
    ...
    [<SSCChart: pump-single Challenge 21>]

Much like simfiles, charts have their own "known properties" like :code:`meter`
and :code:`stepstype` which can be fetched via attributes, as well as a backing
:code:`OrderedDict` which maps uppercase keys like :code:`'METER'` and
:code:`'STEPSTYPE'` to the same string values.

.. note::

    While :class:`simfile.sm.SMChart` uses the same :code:`OrderedDict` backing
    as the other classes, its keys are fixed because SM charts are encoded
    as a list of six properties. Of course, all six of these properties are
    "known properties" with convenience attributes, so the only reason to use
    the dictionary interface is when it's convenient for compatibility with SSC
    charts, or when you want to iterate over the properties.

Editing simfile data
--------------------

Simfile and chart objects are mutable: you can add, change, and delete
properties and charts through the usual Python mechanisms.

Changes to known properties are kept in sync between the attribute and key
lookups; the attributes are Python properties that use the key lookup behind
the scenes.

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> springtime.subtitle = '(edited)'
    >>> springtime
    <SSCSimfile: Springtime (edited)>
    >>> springtime.charts.append(SMChart())
    >>> len(springtime.charts)
    10
    >>> del springtime.displaybpm
    >>> 'DISPLAYBPM' in springtime
    False

If you want to change more complicated data structures like timing and note
data, refer to :ref:`timing-note-data` for an overview of the available classes
& functions, rather than operating on the string values directly.

.. doctest::

    >>> import simfile
    >>> from simfile.notes import NoteData
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> note_data = NoteData.from_chart(springtime.charts[0])
    >>> # (modify the note data)
    >>> note_data.update_chart(springtime.charts[0])

Writing simfiles to disk
------------------------

There are a few options for saving simfiles to the filesystem. If you want to
read simfiles from the disk, modify them, and then save them, you can use the
:func:`simfile.mutate` context manager:

    >>> import simfile
    >>> with simfile.mutate('testdata/Springtime.ssc') as springtime:
    ...     if springtime.subtitle.endswith('(edited)'):
    ...         raise simfile.CancelMutation
    ...     springtime.subtitle += '(edited)'

:func:`simfile.mutate` writes the simfile back to the disk only if it exits
without an exception. Any exception that reaches the context manager will
propagate up, *except* for :class:`.CancelMutation`, which cancels the
operation without re-throwing.

If this workflow doesn't suit your use case, you can serialize to a file object
using the simfile's :meth:`~simfile.base.BaseSimfile.serialize` method:

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> springtime.subtitle = '(edited)'
    >>> with open('testdata/Springtime (edit).ssc', 'w', encoding='utf-8') as outfile:
    ...     springtime.serialize(outfile)

Finally, if your destination isn't a file object, you can serialize the simfile
to a string using :code:`str(simfile)` and proceed from there.