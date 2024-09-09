.. _changelog:

Changelog
=========

3.0.0a1
-------

Breaking changes
~~~~~~~~~~~~~~~~

.. warning::

    **simfile** 3.0 introduces some breaking changes
    that you may need to update your code to handle:

    **Python 3.10 or higher required**

    **simfile**'s minimum Python version was raised from 3.6 to 3.10.

    ----

    **Strict parsing is now off by default**

    Functions in the top-level module,
    such as :func:`simfile.open`, :func:`simfile.load`, and :func:`simfile.mutate`,
    now default to ``strict=False``.
    If you want strict parse errors,
    pass ``strict=True`` to restore the old behavior.
    
    **Features that are now optional**

    The :mod:`simfile.assets` submodule
    now requires installing **simfile** with the ``assets`` extra.
    Run one of these commands to add it to your project::
      
      pip install 'simfile[assets]'  # or...
      poetry add 'simfile[assets]'  # or...
      rye add simfile --features assets
        
    The `filesystem` parameter of various functions & methods
    now requires installing **simfile** with the ``fs`` extra.
    Run one of these commands to add it to your project::

      pip install 'simfile[fs]'  # or...
      poetry add 'simfile[fs]'  # or...
      rye add simfile --features fs
      
    If you want to use both of these optional features,
    join them with a comma::

      pip install 'simfile[assets,fs]'  # or...
      poetry add 'simfile[assets,fs]'  # or...
      rye add simfile --features assets,fs
    
    **Some dict operations no longer supported on simfiles & charts**

    The :data:`.Simfile` and :data:`.Chart` classes (both SM and SSC)
    no longer inherit OrderedDict;
    instead, they have a private OrderedDict attribute
    and forward common dictionary methods & operations to it.
    
    These operations that were previously inherited
    by :data:`.Simfile` and :data:`.Chart`
    are **not** forwarded:
    
    * The ``clear``, ``copy``, ``popitem``, ``reversed``, ``setdefault``,
      and ``update`` methods from ``dict`` are no longer supported.
    * The ``|`` and ``|=`` operators are no longer supported.
    
    These operations **are** forwarded and should behave the same as before:
    
    * ``[key]`` indexing & assignment
    * ``len()`` and iteration
    * The ``move_to_end`` method from ``OrderedDict``
    * The ``keys``, ``values``, ``items``, ``get``, and ``pop`` methods from ``dict``

    **TimingData and displaybpm parameters changed**

    :class:`.TimingData` and :func:`.displaybpm` both now take a single argument,
    a :data:`.Simfile` *or* an :data:`.AttachedChart`
    (a chart taken from a :data:`.Simfile` - more on this below).
    Previously, they took one or two arguments,
    a required :data:`.Simfile` and an optional :class:`.Chart`.

    If your code passed both a :data:`.Simfile` and a :class:`.Chart`
    to either of these classes/functions,
    you can probably fix it by removing the first argument (the simfile).
    However, this might not work if your :class:`.Chart` is not an :data:`.AttachedChart`.
    In that case, append your chart to the simfile's :attr:`~.BaseSimfile.charts`
    to *attach* it to the simfile.
    Then you can read the attached chart back from the simfile's :attr:`~.BaseSimfile.charts`.

    **group_notes' "include_note_types" argument removed**

    :func:`.group_notes`' optional `include_note_types` parameter was removed.
    Use the built-in ``filter`` function on the input note data instead.

    It was unclear how this parameter interacted with the other parameters.
    The fact that such a simple operation was included as a parameter
    suggested that it would do something "smarter" under the hood.
    Consequently, it was very easy to make mistakes
    like excluding :data:`.NoteType.TAIL` while setting `join_heads_to_tails` to `True`.
    Other submodules of **simfile** that used :func:`.group_notes` under the hood
    even made mistakes like these!


Uncategorized
~~~~~~~~~~~~~

All charts under a simfile's :attr:`~.charts` attribute
are now instances of :data:`.AttachedChart`,
which is a type union for :class:`.AttachedSMChart` and :class:`.AttachedSSCChart`.
These are subclasses of :class:`.SMChart` and :class:`.SSCChart`
that store a reference to the simfile they came from.

* The plural :class:`.SMCharts` and :class:`.SSCCharts` classes
  are now lists of :class:`.AttachedSMChart` and :class:`.AttachedSSCChart` objects,
  respectively.
  These are subclasses of :class:`.SMChart` and :class:`.SSCChart`
  that store the simfile they came from under the :attr:`~.simfile` attribute.
  Adding a detached :class:`.SMChart` or :class:`.SSCChart` object
  to a :class:`.SMCharts` or :class:`.SSCCharts` list
  will create an attached copy and add that to the list instead.

New features
~~~~~~~~~~~~


Enhancements
~~~~~~~~~~~~

Deserializing and serializing a :data:`.Simfile` is now byte-for-byte symmetric.
For example,
if you open a simfile with :func:`simfile.mutate`
and don't make any changes,
the output file will exactly match the input file.
This includes whitespace, comments, and any other ephemeral details.

Bugfixes
~~~~~~~~



2.1.1
-----

Bugfixes
~~~~~~~~

Two bugs in **simfile** 2.1.0's SSC implementation broke multi-value properties,
causing them to be truncated or mangled past the first value.
This release fixes these issues:

1. When opening an SSC file,
   the `DISPLAYBPM` and `ATTACKS` properties of both simfiles and charts
   no longer stop parsing at the first ``:``.
   For `DISPLAYBPM`, this meant a BPM range of ``120:240``
   would have been incorrectly parsed as a static BPM of ``120``.
   `ATTACKS` were completely broken as they use colon as a separator.
2. The aforementioned properties are now correctly serialized from :class:`.SSCChart`;
   previously, they would have been escaped with backslashes.
   This bug had the same effects described above,
   but only affected manual assignment of multi-value properties
   (e.g. ``chart.displaybpm = "120:240"``)
   since the first bug shadowed this bug during deserialization.

2.1.0
-----

New features
~~~~~~~~~~~~

* The new :mod:`simfile.dir` module offers
  :class:`.SimfileDirectory` and :class:`.SimfilePack` classes
  for nagivating simfile filesystem structures.
* The new :mod:`simfile.assets` module provides an :class:`.Assets` class
  that can reliably discover paths to simfile assets,
  even if they're not specified in the simfile.
* The top-level :mod:`simfile` module
  now offers :func:`.opendir` and :func:`.openpack` functions
  as simplified interfaces to the :mod:`simfile.dir` API.
* `PyFilesystem2 <https://docs.pyfilesystem.org/en/latest/index.html>`_
  has been integrated throughout this library's filesystem interactions,
  enabling OS and non-OS filesystems to be traversed using the same code.
  All functions, methods, and constructors that lead to filesystem interactions
  now have an optional `filesystem` parameter
  for specifying a PyFS filesystem object.
  When omitted, the filesystem defaults to the native OS filesystem as before.
* The :data:`.DisplayBPM` classes now all expose the same four properties;
  the ones that don't apply to a particular class return None.
  This enables you to handle all three cases
  without having to import the types for ``isinstance`` checks.
  Refer to :ref:`getting-the-displayed-bpm` for more details.

Bugfixes
~~~~~~~~

* The :data:`.charts` property on simfiles is now writable,
  meaning the list of charts can be overwritten directly
  (not just added to / removed from).
* Backslash escape sequences and multi-value MSD parameters
  are now handled correctly,
  both when opening and serializing simfiles.
  See the Enhancements section below for more details.
* :func:`.sm_to_ssc` no longer produces invalid output
  when there are negative BPMs or stops in the timing data.
  (It throws ``NotImplementedError`` as a temporary stopgap.
  In the future, negative timing data will be converted to warps,
  as StepMania does automatically.)
* Various type annotations have been improved throughout the library.
  In particular, ``Iterator`` input arguments
  have been replaced with ``Iterable``
  so that you don't need to wrap them in ``iter(...)``
  to suppress type errors from static analyzers.

Enhancements
~~~~~~~~~~~~

* The dependency on `msdparser <https://msdparser.readthedocs.io/en/latest/>`_
  has been upgraded to version 2.
  This corrects parsing of escape sequences and multi-value parameters,
  meaning that ``:`` and ``\`` characters inside a value
  are handled the same way as in StepMania.
  Additionally, parsing is now up to 10 times faster than before!

2.0.1
-----

**Bugfix:**
The dependency on msdparser 1.0.0 was mis-specified
in both the Pipfile and setup.py.
Publishing msdparser 2.0.0-beta.3 (a breaking release)
caused fresh installs to be broken.
This patch fixes the version specification in both files.

2.0.0
-----

Initial stable release of version 2.
Refer to :ref:`migrating` for a general overview of the changes
since version 1.