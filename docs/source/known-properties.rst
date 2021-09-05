.. _known-properties:

Known properties
================

*Known properties* refer to properties of simfiles and their charts that the
current stable version of StepMania actively uses. These are the properties
that **simfile** exposes as attributes on simfile and chart objects. They are
also the only properties that StepMania's built-in editor will preserve when
saving a simfile; unknown properties are liable to be deleted if saved by the
StepMania editor.

When working with known properties, you should prefer to use attributes (e.g.
:code:`sim.title`, :code:`chart.stepstype`) rather than indexing into the
underlying dictionary (e.g. :code:`sim['TITLE']`, :code:`chart['STEPSTYPE']`).
While these are functionally equivalent in many cases, attributes generally
behave closer to how StepMania interprets simfiles:

* If a property is missing from the simfile, accessing the attribute returns
  None instead of throwing a :code:`KeyError`. StepMania generally treats
  missing properties as if they had an empty or default value, so it's nice
  to be able to handle this case without having to catch exceptions everywhere.
* StepMania supports a few legacy aliases for properties, and attributes make
  use of these aliases when present. For example, if a simfile contains a
  :code:`FREEZES` property instead of the usual :code:`STOPS`, :code:`sim.stops`
  will use the alias in the backing dictionary (both for reads and writes!),
  whereas :code:`sim['STOPS']` will throw a :code:`KeyError`. This lets you
  write cleaner code with fewer special cases for old simfiles.
* Attributes are implicitly spell-checked: misspelling a property like
  :code:`sim.artistranslit` will consistently raise an :code:`AttributeError`,
  and may even be flagged by your IDE depending on its Python type-checking
  capabilities. By contrast, reading from :code:`sim['ARTISTRANSLIT']` will
  generally raise the more vague :code:`KeyError` exception, and writing to
  such a field would create a new, unknown property in the simfile, which is
  probably not what you wanted. Furthermore, your IDE would have no way to
  know the string property is misspelled.

With that said, there are legitimate use cases for indexing. String keys are
easier when you need to operate on multiple properties generically, and they're
the only option for accessing "unknown properties" like numbered
:code:`BGCHANGES` and properties only used by derivatives of StepMania.
When dealing with property string keys, consider using the :code:`.get` method
from the underlying dictionary to handle missing keys gracefully.

What are the known properties?
------------------------------

These are the known properties for simfiles:

================ ================ ========= ==========
String key       Attribute        SMSimfile SSCSimfile
================ ================ ========= ==========
TITLE            title            ✓         ✓
SUBTITLE         subtitle         ✓         ✓
ARTIST           artist           ✓         ✓
TITLETRANSLIT    titletranslit    ✓         ✓
SUBTITLETRANSLIT subtitletranslit ✓         ✓
ARTISTTRANSLIT   artisttranslit   ✓         ✓
GENRE            genre            ✓         ✓
CREDIT           credit           ✓         ✓
BANNER           banner           ✓         ✓
BACKGROUND       background       ✓         ✓
LYRICSPATH       lyricspath       ✓         ✓
CDTITLE          cdtitle          ✓         ✓
MUSIC            music            ✓         ✓
OFFSET           offset           ✓         ✓
BPMS             bpms             ✓         ✓
STOPS            stops            ✓         ✓
FREEZES [1]_     stops            ✓         
DELAYS           delays           ✓         ✓
TIMESIGNATURES   timesignatures   ✓         ✓
TICKCOUNTS       tickcounts       ✓         ✓
INSTRUMENTTRACK  instrumenttrack  ✓         ✓
SAMPLESTART      samplestart      ✓         ✓
SAMPLELENGTH     samplelength     ✓         ✓
DISPLAYBPM       displaybpm       ✓         ✓
SELECTABLE       selectable       ✓         ✓
BGCHANGES        bgchanges        ✓         ✓
ANIMATIONS [1]_  bgchanges        ✓         ✓
FGCHANGES        fgchanges        ✓         ✓
KEYSOUNDS        keysounds        ✓         ✓
ATTACKS          attacks          ✓         ✓
VERSION          version                    ✓
ORIGIN           origin                     ✓
PREVIEWVID       previewvid                 ✓
JACKET           jacket                     ✓
CDIMAGE          cdimage                    ✓
DISCIMAGE        discimage                  ✓
PREVIEW          preview                    ✓
MUSICLENGTH      musiclength                ✓
LASTSECONDHINT   lastsecondhint             ✓
WARPS            warps                      ✓
LABELS           labels                     ✓
COMBOS           combos                     ✓
SPEEDS           speeds                     ✓
SCROLLS          scrolls                    ✓
FAKES            fakes                      ✓
================ ================ ========= ==========

And these are the known properties for charts:

================ ================ ======= ========
String key       Attribute        SMChart SSCChart
================ ================ ======= ========
STEPSTYPE        stepstype        ✓       ✓
DESCRIPTION      description      ✓       ✓
DIFFICULTY       difficulty       ✓       ✓
METER            meter            ✓       ✓
RADARVALUES      radarvalues      ✓       ✓
NOTES            notes            ✓       ✓
NOTES2 [1]_      notes                    ✓
CHARTNAME        chartname                ✓
CHARTSTYLE       chartstyle               ✓
CREDIT           credit                   ✓
MUSIC            music                    ✓
BPMS             bpms                     ✓
STOPS            stops                    ✓
DELAYS           delays                   ✓
TIMESIGNATURES   timesignatures           ✓
TICKCOUNTS       tickcounts               ✓
COMBOS           combos                   ✓
WARPS            warps                    ✓
SPEEDS           speeds                   ✓
SCROLLS          scrolls                  ✓
FAKES            fakes                    ✓
LABELS           labels                   ✓
ATTACKS          attacks                  ✓
OFFSET           offset                   ✓
DISPLAYBPM       displaybpm               ✓
================ ================ ======= ========

.. [1] These keys are aliases supported by StepMania. The attribute will only
       use the alias if it's present in the backing dictionary and the standard
       name is not.

Known properties supported by both the SM and SSC formats are documented in
:class:`.BaseSimfile` and :class:`.BaseChart`. These are exactly
the known properties for :class:`.SMSimfile` and :class:`.SMChart`. The SSC
format then adds additional known properties on top of the base set.

Here is all of the relevant documentation:

.. autoclass:: simfile.base.BaseSimfile
    :noindex:
.. autoclass:: simfile.base.BaseChart
    :noindex:
.. autoclass:: simfile.ssc.SSCSimfile
    :noindex:
.. autoclass:: simfile.ssc.SSCChart
    :noindex:
