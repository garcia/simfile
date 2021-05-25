.. _changelog:

Changelog
=========

2.0.0-beta.2
------------

Breaking changes
~~~~~~~~~~~~~~~~

* :code:`simfile.notes.timed.timed_note_generator` was renamed to
  :func:`simfile.notes.timed.time_notes` to bring it in parity with the other
  "verb functions" like :func:`simfile.notes.group.group_notes` and
  :func:`simfile.notes.count.count_grouped_notes`.

New features
~~~~~~~~~~~~

* :func:`simfile.notes.timed.time_notes` now takes an `unhittable_notes`
  parameter that determines the behavior for notes inside warp segments.


Bugfixes
~~~~~~~~

These changes fix parsing of some real simfiles that StepMania accepts but
:code:`simfile` previously raised an exception for:

* :class:`simfile.sm.SMChart` now allows more than 6 chart components. Any
  extra components are stored in a new :data:`simfile.sm.SMChart.extradata`
  attribute and are returned to the end of the chart upon serialization.
* :class:`simfile.notes.NoteData` now strips whitespace from both sides of each
  row in the note data, not just from the end of the line.
* :class:`simfile.timing.TimingData` now defaults the offset to 0 when it's not
  specified in the simfile and/or chart.

Miscellaneous
~~~~~~~~~~~~~

* :meth:`simfile.timing.TimingData.from_simfile`'s `ssc_chart` parameter was
  renamed to `chart` and its type annotation widened from
  :class:`simfile.ssc.SSCChart` to :data:`simfile.types.Chart` to better
  accommodate code that's agnostic to the simfile type.

2.0.0-beta.1
------------

First beta release of version 2.0. Refer to :ref:`migrating` for a general
overview of the changes since version 1.0.