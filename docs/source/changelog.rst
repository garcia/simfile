.. _changelog:

Changelog
=========

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
:code:`simfile` previously raised an exception for:

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