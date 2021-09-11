.. _reading-writing:

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
    >>> print(springtime.title)
    Springtime

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
    >>> kryptix = simfile.open('testdata/Kryptix.sm')
    >>> type(kryptix)
    <class 'simfile.sm.SMSimfile'>

The "magic" that determines which type to use is documented under
:func:`simfile.load`. If you'd rather use the underlying types directly,
instantiate them with either a `file` or `string` argument:

.. doctest::

    >>> from simfile.ssc import SSCSimfile
    >>> with open('testdata/Springtime.ssc', 'r') as infile:
    ...     springtime = SSCSimfile(file=infile)

Note that the underlying simfile types don't know about the filesystem: you
can't pass them a filename directly, nor do they offer a :code:`.save()`
method. This is different from how version 1.0 of this package worked; refer to
:ref:`migrating` for more details on the differences.

Accessing simfile properties
----------------------------

Earlier we used the :attr:`~.BaseSimfile.title` attribute to get a simfile's
title. Many other properties are exposed as attributes as well:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> springtime.music
    'Kommisar - Springtime.mp3'
    >>> springtime.samplestart
    '105.760'
    >>> springtime.labels
    '0=Song Start'

Refer to :ref:`known-properties` for the full list of attributes for each
simfile format. Many properties are shared between the SM and SSC formats, so
you can use them without checking what kind of :data:`.Simfile` or
:data:`.Chart` you have.

Attributes are great, but they can't cover *every* property found in every
simfile in existence. When you need to deal with unknown properties, you can
use any simfile or chart as a dictionary of uppercase property names (they all
extend :code:`OrderedDict` under the hood):

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc')
    >>> springtime['ARTIST']
    'Kommisar'
    >>> springtime['ARTIST'] is springtime.artist
    True
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

Stepcharts don't follow the same key-value convention as other simfile
properties; a simfile can have zero to many charts. The charts are stored in a
list under the :attr:`~.BaseSimfile.charts` attribute:

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

    The keys of an :class:`~simfile.sm.SMChart` are **fixed** because SM charts
    are encoded as a list of six properties. Of course, all six of these
    properties are "known" and thus exposed through attributes, so it's rare to
    need to use the underlying dictionary interface for this class.

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
    >>> first_chart = springtime.charts[0]
    >>> notedata = NoteData(first_chart)
    >>> # (...modify the note data...)
    >>> first_chart.notes = str(notedata)

Writing simfiles to disk
------------------------

There are a few options for saving simfiles to the filesystem. If you want to
read simfiles from the disk, modify them, and then save them, you can use the
:func:`simfile.mutate` context manager:

    >>> import simfile
    >>> input_filename = 'testdata/Springtime.ssc'
    >>> with simfile.mutate(
    ...     input_filename,
    ...     backup_filename=f'{input_filename}.old',
    ... ) as springtime:
    ...     if springtime.subtitle.endswith('(edited)'):
    ...         raise simfile.CancelMutation
    ...     springtime.subtitle += '(edited)'

In this example, we specify the optional `backup_filename` parameter to
preserve the simfile's original contents. Alternatively, we could have
specified an `output_filename` to write the modified simfile somewhere other
than the input filename.

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

Robust parsing of arbitrary simfiles
------------------------------------

The real world is messy, and many simfiles on the Internet are technically
malformed despite appearing to function correctly in StepMania. This library
aims to be **strict by default**, both for input and output, but allow more
permissive input handling on an opt-in basis.

The functions exposed by the top-level :mod:`simfile` module accept a `strict`
parameter that can be set to False to suppress MSD parser errors:

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime.ssc', strict=False)

.. warning::

    Due to the simplicity of the MSD format, there's only one error condition
    at the data layer - stray text between parameters - which setting `strict`
    to False suppresses. Almost any text file will successfully parse as a
    "simfile" with this check disabled, so exercise caution when applying this
    feature to arbitrary files.

While most modern simfiles are encoded in UTF-8, many older simfiles use dated
encodings (perhaps resembling Latin-1 or Shift-JIS). This was a pain to handle
correctly in older versions, but in version 2.0, all :mod:`simfile` functions
that interact with the filesystem detect an appropriate encoding automatically,
so there's typically no need to specify an encoding or handle
:code:`UnicodeDecodeError` exceptions. Read through the documentation of
:func:`.open_with_detected_encoding` for more details.

When grouping notes using the :func:`.group_notes` function,
orphaned head or tail notes will raise an exception by default. Refer to
:ref:`handling-holds-rolls-jumps` for more information on handling orphaned
notes gracefully. (This is more common than you might imagine - "Springtime",
which comes bunded with StepMania, has orphaned tail notes in its first chart!)