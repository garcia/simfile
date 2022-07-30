.. _reading-writing:

Reading & writing simfiles
==========================

Opening simfiles
----------------

The top-level :mod:`simfile` module offers 3 convenience functions for loading
simfiles from the filesystem, depending on what kind of filename you have:

* :func:`simfile.open` takes a path to an SM or SSC file.
* :func:`simfile.opendir` takes a path to a simfile directory. *(new in 2.1)*
* :func:`simfile.openpack` takes a path to a simfile pack. *(new in 2.1)*

.. doctest::

    >>> import simfile
    >>> springtime1 = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> springtime2, filename = simfile.opendir('testdata/Springtime')
    >>> for sim, filename in simfile.openpack('testdata'):
    ...     if sim.title == 'Springtime':
    ...         springtime3 = sim
    ...
    >>> print springtime1 == springtime2 and springtime2 == springtime3
    True

Plus two more that don't take filenames:

* :func:`simfile.load` takes a file object.
* :func:`simfile.loads` takes a string of simfile data.

.. note::

    If you're about to write this:

    .. code:: python
        
        with open('path/to/simfile.sm', 'r') as infile:
            sim = simfile.load(infile)
    
    Consider writing ``simfile.open('path/to/simfile.sm')`` instead.
    This is equivalent, but shorter and easier to remember.
    It also lets **simfile** determine the filetype by extension,
    rather than having to tee the file to look for a `VERSION` tag.

The type returned by functions like :func:`.open` and :func:`.load` is declared
as :data:`.Simfile`. This is a union of the two concrete simfile
types, :class:`.SMSimfile` and :class:`.SSCSimfile`:

 .. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> type(springtime)
    <class 'simfile.ssc.SSCSimfile'>
    >>> nekonabe = simfile.open('testdata/nekonabe/nekonabe.sm')
    >>> type(nekonabe)
    <class 'simfile.sm.SMSimfile'>

The "magic" that determines which type to use is documented under
:func:`simfile.load`. If you'd rather use the underlying types directly,
instantiate them with either a `file` or `string` argument:

.. doctest::

    >>> from simfile.ssc import SSCSimfile
    >>> with open('testdata/Springtime/Springtime.ssc', 'r') as infile:
    ...     springtime = SSCSimfile(file=infile)

.. note::

    These :data:`.Simfile` types don't know about the filesystem; you can't
    pass them a filename directly, nor do they offer a :code:`.save()`
    method (see :ref:`writing-simfiles-to-disk` for alternatives).
    Decoupling this knowledge from the simfile itself enables them to
    live in-memory, without a corresponding file and without introducing
    state-specific functionality to the core simfile classes.

Accessing simfile properties
----------------------------

Earlier we used the :attr:`~.BaseSimfile.title` attribute to get a simfile's
title. Many other properties are exposed as attributes as well:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
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

All properties return a string value,
or None if the property is missing.
The possibility of None can be annoying in type-checked code,
so you may want to write expressions like ``sf.title or ""``
to guarantee a string.

Attributes are great, but they can't cover *every* property found in every
simfile in existence. When you need to deal with unknown properties, you can
use any simfile or chart as a dictionary of uppercase property names (they all
extend :code:`OrderedDict` under the hood):

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
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

Charts are different from regular properties,
because a simfile can have zero to many charts.
The charts are stored in a list
under the :attr:`~.BaseSimfile.charts` attribute:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> len(springtime.charts)
    9
    >>> springtime.charts[0]
    <SSCChart: dance-single Challenge 12>

To find a particular chart, use a for-loop
or Python's built-in :code:`filter` function:

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
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

.. warning::

    Even the :attr:`~.BaseChart.meter` property is a string!
    Some simfiles in the wild have a non-numeric meter due to manual editing;
    it's up to client code to determine how to deal with this.

    If you need to compare meters numerically,
    you can use ``int(chart.meter)``,
    or ``int(chart.meter or '1')`` to sate type-checkers like mypy.

Editing simfile data
--------------------

Simfile and chart objects are mutable: you can add, change, and delete
properties and charts through the usual Python mechanisms.

Changes to known properties are kept in sync between the attribute and key
lookups; the attributes are Python properties that use the key lookup behind
the scenes.

.. doctest::

    >>> import simfile
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
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
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
    >>> first_chart = springtime.charts[0]
    >>> notedata = NoteData(first_chart)
    >>> # (...modify the note data...)
    >>> first_chart.notes = str(notedata)

.. note::

    The keys of an :class:`~simfile.sm.SMChart` are static;
    they can't be added or removed,
    but their values can be replaced.

.. _writing-simfiles-to-disk:

Writing simfiles to disk
------------------------

There are a few options for saving simfiles to the filesystem. If you want to
read simfiles from the disk, modify them, and then save them, you can use the
:func:`simfile.mutate` context manager:

    >>> import simfile
    >>> input_filename = 'testdata/Springtime/Springtime.ssc'
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
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
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
    >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc', strict=False)

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