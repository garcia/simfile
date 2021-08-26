.. _known-properties:

Known properties
================

*Known properties* refer to properties of simfiles and their charts that the
current stable version of StepMania actively uses. These are the properties
that StepMania's built-in editor will preserve when it saves a simfile that was
loaded from disk; any unknown properties will be lost if overwritten by the
editor.

**simfile** enables you to access properties of simfiles & charts in a few
different ways:

* **Indexing** (e.g. :code:`sim['TITLE']`, :code:`chart['STEPSTYPE']`) provides
  access to all properties via uppercase names. (They're converted to uppercase
  so you don't need to!)

  - Both indexing and **.get()** (e.g. :code:`sim.get('TITLE')`,
    :code:`chart.get('STEPSTYPE')`) are features of the underlying
    :code:`OrderedDict`. You may prefer to use .get() to handle missing
    properties without having to catch a :code:`KeyError`.

* **Attributes** (e.g. :code:`sim.title`, :code:`chart.stepstype`) provide
  access to *known properties* via lowercase names. Like .get(), missing
  properties return None.

All of these options have their benefits and drawbacks. Indexing is a quick &
intuitive way to access any property; .get() can handle any property, even if
it's missing; attributes, though limited to known properties, are implicitly
spell-checked and arguably look the nicest in code. Both indexing and
attributes can handle reads, writes, and deletes, and all methods are backed by
the same data structure.

What are the known properties?
------------------------------

These are the known properties for simfiles:

================ ===================== ========= ==========
Uppercase (key)  Lowercase (attribute) SMSimfile SSCSimfile 
================ ===================== ========= ==========
TITLE            title                 ✓         ✓
SUBTITLE         subtitle              ✓         ✓
ARTIST           artist                ✓         ✓
TITLETRANSLIT    titletranslit         ✓         ✓
SUBTITLETRANSLIT subtitletranslit      ✓         ✓
ARTISTTRANSLIT   artisttranslit        ✓         ✓
GENRE            genre                 ✓         ✓
CREDIT           credit                ✓         ✓
BANNER           banner                ✓         ✓
BACKGROUND       background            ✓         ✓
LYRICSPATH       lyricspath            ✓         ✓
CDTITLE          cdtitle               ✓         ✓
MUSIC            music                 ✓         ✓
OFFSET           offset                ✓         ✓
BPMS             bpms                  ✓         ✓
STOPS            stops                 ✓ [1]_    ✓
DELAYS           delays                ✓         ✓
TIMESIGNATURES   timesignatures        ✓         ✓
TICKCOUNTS       tickcounts            ✓         ✓
INSTRUMENTTRACK  instrumenttrack       ✓         ✓
SAMPLESTART      samplestart           ✓         ✓
SAMPLELENGTH     samplelength          ✓         ✓
DISPLAYBPM       displaybpm            ✓         ✓
SELECTABLE       selectable            ✓         ✓
BGCHANGES        bgchanges             ✓ [2]_    ✓ [2]_
FGCHANGES        fgchanges             ✓         ✓
KEYSOUNDS        keysounds             ✓         ✓
ATTACKS          attacks               ✓         ✓
VERSION          version                         ✓
ORIGIN           origin                          ✓
PREVIEWVID       previewvid                      ✓
JACKET           jacket                          ✓
CDIMAGE          cdimage                         ✓
DISCIMAGE        discimage                       ✓
WARPS            warps                           ✓
COMBOS           combos                          ✓
SPEEDS           speeds                          ✓
SCROLLS          scrolls                         ✓
FAKES            fakes                           ✓
LABELS           labels                          ✓
================ ===================== ========= ==========

.. [1] SM files support "FREEZES" as an alias for "STOPS". The property name is
       converted during parsing, so no extra logic is required to handle this.
.. [2] SM and SSC files support "ANIMATIONS" as an alias for "BGCHANGES". As
       above, the property name is converted during parsing.

And these are the known properties for charts:

================ ===================== ======= ========
Uppercase (key)  Lowercase (attribute) SMChart SSCChart
================ ===================== ======= ========
STEPSTYPE        stepstype             ✓       ✓
DESCRIPTION      description           ✓       ✓
DIFFICULTY       difficulty            ✓       ✓
METER            meter                 ✓       ✓
RADARVALUES      radarvalues           ✓       ✓
NOTES            notes                 ✓       ✓
CHARTNAME        chartname                     ✓
CHARTSTYLE       chartstyle                    ✓
CREDIT           credit                        ✓
MUSIC            music                         ✓
BPMS             bpms                          ✓
STOPS            stops                         ✓
DELAYS           delays                        ✓
TIMESIGNATURES   timesignatures                ✓
TICKCOUNTS       tickcounts                    ✓
COMBOS           combos                        ✓
WARPS            warps                         ✓
SPEEDS           speeds                        ✓
SCROLLS          scrolls                       ✓
FAKES            fakes                         ✓
LABELS           labels                        ✓
ATTACKS          attacks                       ✓
OFFSET           offset                        ✓
DISPLAYBPM       displaybpm                    ✓
================ ===================== ======= ========

First, all simfiles & charts have a shared subset of known properties,
documented in :class:`.BaseSimfile` and :class:`.BaseChart`. These are exactly
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
