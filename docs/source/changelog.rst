.. _changelog:

Changelog
=========

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
  without having to import the types for ``instanceof`` checks.
  Refer to :ref:`displayed-bpm` for more details.

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