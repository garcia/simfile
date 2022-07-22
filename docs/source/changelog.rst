.. _changelog:

Changelog
=========

2.1.0-rc.1
----------

* The :data:`.DisplayBPM` classes now all expose the same four properties;
  the ones that don't apply to a particular class return None.
  This enables you to handle all three cases without having to import the
  types for :code:`instanceof()` checks.

2.1.0-beta.3
------------

New features
~~~~~~~~~~~~

* The new :mod:`simfile.dir` module offers :class:`.SimfileDirectory` and
  :class:`.SimfilePack` classes for nagivating simfile filesystem structures.
* The new :mod:`simfile.assets` module provides an :class:`.Assets` class that
  can reliably discover paths to simfile assets, even if they're not specified
  in the simfile.
* `PyFilesystem2 <https://docs.pyfilesystem.org/en/latest/index.html>`_ has
  been integrated throughout this library's filesystem interactions, enabling
  OS and non-OS filesystems to be traversed using the same code. All functions,
  methods, and constructors that lead to filesystem interactions now have an
  optional :code:`filesystem` parameter for specifying a PyFS filesystem
  object. When omitted, the filesystem defaults to the native OS filesystem as
  before.

Bugfixes
~~~~~~~~

* The :data:`.charts` property on simfiles is now writable, meaning the list
  of charts can be overwritten directly (not just added to / removed from).
* Backslash escape sequences and multi-value MSD parameters are now handled
  correctly, both when opening and serializing simfiles. Previously,
  backslashes and any colons after the key-value separator were treated as
  regular text.
* :func:`.sm_to_ssc` no longer produces invalid output when there are negative
  BPMs or stops in the timing data. (It throws :code:`NotImplementedError` as
  a temporary stopgap. In the future, negative timing data will be converted to
  warps, as StepMania does automatically.)

2.0.1
-----

Bugfixes
~~~~~~~~

* The dependency on msdparser 1.0.0 was mis-specified in both the Pipfile and
  setup.py. Publishing msdparser 2.0.0-beta.3 (a breaking release) caused
  fresh installs to be broken. This patch fixes the version specification in
  both files.

2.0.0
-----

Stable release. No changes from the release candidate below.

2.0.0-rc.1
----------

Breaking changes
~~~~~~~~~~~~~~~~

* The classmethods :code:`NoteData.from_chart` and
  :code:`TimingData.from_simfile` have been removed in favor of the
  :class:`.NoteData` and :class:`.TimingData` constructors. Simply remove
  :code:`.from_simfile` or :code:`.from_chart` to use the constructor instead.
* The instance method :code:`NoteData.update_chart` has been removed in favor
  of the more intuitive pattern :code:`chart.notes = str(notedata)`. The method
  only existed because keysounded charts (for which note data is stored in the
  :code:`NOTES2` property instead of :code:`NOTES`) would have required extra
  code to update properly. With the advent of property aliases, this is no
  longer necessary, as references to the :attr:`~.BaseChart.notes` attribute
  will identify the correct underlying property.

2.0.0-beta.7
------------

Breaking changes
~~~~~~~~~~~~~~~~

* The enum :code:`simfile.convert.KnownProperty` was renamed to
  :class:`PropertyType` to reflect its semantics better.

New features
~~~~~~~~~~~~

* Simfiles and charts now support the same property aliases that StepMania
  implements, namely :code:`FREEZES` (SM only), :code:`ANIMATIONS` (SM and
  SSC), and :code:`NOTES2` (SSC only). This feature supersedes the more naïve
  implementation from beta 6 where the alias keys :code:`FREEZES` and
  :code:`ANIMATIONS` were converted to the standard name during parsing. See
  :ref:`known-properties` for more information.
* The :class:`.NoteData` constructor now accepts a :data:`.Chart` or another
  :class:`.NoteData` instance, in addition to a string of note data as before.
  This means what previously required typing :code:`NoteData.from_chart(chart)`
  or :code:`NoteData(str(notedata))` can now be accomplished with
  :code:`NoteData(chart)` or :code:`NoteData(notedata)`.
* Converting a :class:`.NoteType` to a string using :code:`str(note_type)` now
  returns the note type's character. Converting a :class:`.Note` to a string
  does the same, followed by a bracketed keysound index if present on the Note.

Bugfixes
~~~~~~~~

* :meth:`.NoteData.from_notes` now makes use of the :attr:`~.Note.player` and
  :attr:`~.Note.keysound_index` attributes on notes, so routine charts &
  keysounded SSC charts can be serialized back into note data correctly.
* :attr:`.NoteData.columns` now handles all keysounded charts correctly.
  Previously, any keysound data on beat 0 would cause this value to be wrong.
* The functions in :mod:`simfile.notes.group` no longer erase
  :attr:`~.Note.player` and :attr:`~.Note.keysound_index` values. As a
  corollary, :class:`.NoteWithTail` now has a
  :attr:`~.NoteWithTail.keysound_index` attribute, bringing it back in parity
  with :class:`.Note`.
* The behavior for :attr:`.InvalidPropertyBehavior.ERROR_UNLESS_DEFAULT` was
  backwards - it would raise an exception *only* if the property value was the
  default. This has been fixed.

Miscellaneous
~~~~~~~~~~~~~

* The known property type mappings in :mod:`simfile.convert` have been updated
  with the full set of known SSC-exclusive properties.

2.0.0-beta.6
------------

New features
~~~~~~~~~~~~

* :class:`.Note` now has a :attr:`~.Note.player` attribute to support routine
  charts, which store the notes for each of the two players separately. This
  attribute will always be 0 for non-routine charts, but will be incremented to
  1 for the second player's notes in routine charts. As a corollary, notes are
  now ordered first by *player*, then by beat and column as before.
* :class:`.Note` now has a :attr:`~.Note.keysound_index` attribute that stores
  any keysound index attached to the note. This only affects keysounded SSC
  charts; in all other cases, this attribute should be None.
* :ref:`known-properties` for simfiles and charts now exactly mirror those
  supported by StepMania as intended:
  
  - Some SSC properties were converted to base properties, because they are
    supported (though not exported by default) in SM files.
  - Some new, non-default properties were added to both SM and SSC simfiles.
  - Music & timing data properties were added to SSC charts.

Bugfixes
~~~~~~~~

* Routine charts now parse correctly.
* Keysounded SSC charts now parse correctly.
* Adding or reordering the properties of an SSC chart was previously liable to
  break the chart in StepMania because the :code:`NOTES` / :code:`NOTES2`
  property is expected to be the last property of the chart. This invariant is
  now enforced during serialization, so SSC properties can be freely modified.

These changes fix parsing of some real simfiles that StepMania accepts but
**simfile** previously handled poorly:

* SM simfiles may now use the :code:`FREEZES` property as an alias for
  :code:`STOPS`. The property key will simply be changed to :code:`STOPS`
  internally, mirroring how StepMania implements this alias in
  `NotesLoaderSM.cpp <https://github.com/stepmania/stepmania/blob/3f64564dd7c62a2f3d9557c1bdb8475fd953abea/src/NotesLoaderSM.cpp#L215>`_.
* SM and SSC simfiles may now use the :code:`ANIMATIONS` property as an alias
  for :code:`BGCHANGES`. As above, the property key will simply be replaced
  internally.

2.0.0-beta.5
------------

New features
~~~~~~~~~~~~

* All functions in the top-level :mod:`simfile` module, as well as
  :class:`.BaseSimfile` and :meth:`.SSCChart.from_str`, now accept a `strict`
  parameter that defaults to True. Setting it to False allows the underlying
  MSD parser to ignore stray text between parameters.

Miscellaneous
~~~~~~~~~~~~~

* :class:`.BaseChart`'s constructor no longer accepts an MSD string; this
  was an undocumented feature only used by test cases, and the semantics were
  unclear due to significant differences between :class:`.SMChart` and
  :class:`.SSCChart`. If you need this (relatively niche) functionality, use
  the classmethods :meth:`.SMChart.from_str` and :meth:`.SSCChart.from_str`.

2.0.0-beta.4
------------

New features
~~~~~~~~~~~~

* :func:`simfile.open` and :func:`simfile.mutate` now try four different
  encodings that StepMania supports when no encoding is explicitly supplied.
* :func:`simfile.mutate` now accepts the optional parameters `output_filename`
  and `backup_filename` for writing to files other than the input file.
* Added the function :func:`simfile.open_with_detected_encoding` which performs
  the same logic described above and returns the detected encoding alongside
  the simfile as a tuple.
* Added the function :func:`.ungroup_notes` which serves as an inverse for
  :func:`.group_notes`.

Miscellaneous
~~~~~~~~~~~~~

* :class:`.Note` instances are now comparable, sorted first by beat, then by
  column.
* Constructing a :class:`.Beat` without an explicit denominator now rounds the
  beat to the nearest :meth:`.tick`. For example, both :code:`Beat(1/3)` and
  :code:`Beat(0.333)` now return the same value as :code:`Beat(1, 3)`, rather
  than inheriting :code:`Fraction`'s exact floating point representation
  behavior. (Explicit denominators are preserved for flexibility's sake.)
* :class:`.Beat` and :class:`.NoteType` now have better :code:`repr()` outputs.
* Mathematical operations on a :class:`.Beat` now return a new :class:`.Beat`,
  rather than its base class :class:`.Fraction`.

2.0.0-beta.3
------------

**Bugfix:** Iterating over :class:`.NoteData` with subdivisions other than
powers of two now returns the expected beats; previously the beats had
unexpectedly large numerators & denominators due to floating-point rounding
errors.

2.0.0-beta.2
------------

Breaking changes
~~~~~~~~~~~~~~~~

* :code:`timed_note_generator()` was renamed to :func:`.time_notes` to bring it
  in parity with the other "verb functions" like :func:`~.group_notes` and
  :func:`~.count_grouped_notes`.
* The way to turn :class:`.BeatValues` into string data is now
  :code:`str(beat_values)`, rather than :code:`beat_values.serialize()`. This
  brings it in line with :class:`.NoteData`, charts, and simfiles;
  :code:`str(obj)` produces the canonical string representation, whereas
  :code:`obj.serialize()` (when available) writes said representation to a file
  object.

New features
~~~~~~~~~~~~

* Added the classmethod :meth:`.NoteData.from_notes` which
  converts a stream of notes into note data.
* Added the method :meth:`.NoteData.update_chart` which replaces
  the provided chart's note data.
* :func:`.time_notes` now takes an `unhittable_notes` parameter that determines
  the behavior for notes inside warp segments.


Bugfixes
~~~~~~~~

* Indexing directly into an :class:`.SMChart` (e.g. :code:`chart['STEPSTYPE']`)
  now works as intended; previously it would always throw an
  :code:`AttributeError` due to a coding error.

These changes fix parsing of some real simfiles that StepMania accepts but
**simfile** previously raised an exception for:

* :class:`.SMChart` now allows more than 6 chart components. Any extra
  components are stored in a new :attr:`.SMChart.extradata` attribute and are
  returned to the end of the chart upon serialization.
* Iterating over :class:`.NoteData` now strips whitespace from both sides of
  each row in the note data, not just from the end of the line.
* :class:`.NoteData` methods that interface with charts now use the
  :code:`NOTES2` property when present so that SSC charts with keysounds can be
  read & updated.
* :attr:`.TimingData.offset` now defaults to 0 when the provided simfile and/or
  chart doesn't specify one.
* When :meth:`.TimingData.from_simfile` receives an SSC simfile and chart, it
  now checks that the :attr:`.SSCSimfile.version` is 0.7 or higher before using
  timing data from the chart, as StepMania ignores split timing from older SSC
  files.

Miscellaneous
~~~~~~~~~~~~~

* :meth:`.TimingData.from_simfile`'s `ssc_chart` parameter was renamed to
  `chart` and its type annotation widened from :class:`.SSCChart` to
  :data:`.Chart` to better accommodate SM/SSC-agnostic code.

2.0.0-beta.1
------------

First beta release of version 2.0. Refer to :ref:`migrating` for a general
overview of the changes since version 1.0.