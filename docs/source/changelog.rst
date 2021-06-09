.. _changelog:

Changelog
=========

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