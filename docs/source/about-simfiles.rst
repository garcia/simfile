.. _about-simfiles:

What are simfiles?
==================

Simfiles are the primary unit of game content
for music game simulators like StepMania.
These files contain song metadata and some number of charts
(also known as "stepcharts" or "maps")
that dictate the gameplay sequence.
They are accompanied by a music file
and often some graphic files like banners and backgrounds.

StepMania primarily uses two simfile formats, SM and SSC.
These are the two simfile formats supported by the **simfile** library.

What's in a simfile?
--------------------

If you open a simfile in a text editor, you'll typically be greeted with
something like this:

.. code-block:: text

    #VERSION:0.83;
    #TITLE:Springtime;
    #SUBTITLE:;
    #ARTIST:Kommisar;
    #TITLETRANSLIT:;
    #SUBTITLETRANSLIT:;
    #ARTISTTRANSLIT:;
    #GENRE:;
    #ORIGIN:;
    #CREDIT:;
    #BANNER:springbn.png;
    #BACKGROUND:spring.png;
    [...]

StepMania uses this information to determine how to display the simfile
in-game. Later in the file you'll see *timing data*, which determines how to
keep simfile and audio synchronized, followed by charts containing *note data*,
which contains the input sequence for the player to perform. Charts are
typically written by humans to follow the rhythm of the song.

Why do I need a library for this?
---------------------------------

While the file format shown above seems simple,
simfiles on the Internet vary greatly in formatting and data quality,
and StepMania tries its hardest to support all of these files.
As a result, there are numerous edge cases and undocumented features
that complicate parsing of arbitrary simfiles.
Here are some examples:

* Not all simfiles are encoded in UTF-8;
  many older files from around the world use Windows code pages instead.
  StepMania tries four encodings (UTF-8 followed by three code pages)
  in order until one succeeds.
  
  - :func:`simfile.open` and related functions do the same.

* Many simfiles, even modern ones,
  contain formatting errors such as malformed comments and missing semicolons.
  StepMania handles missing semicolons at the protocol level
  and emits a warning for other formatting errors.

  - :func:`simfile.open` and related functions offer a `strict` parameter
    that can be set to ``False`` to ignore formatting errors.

* Holds and rolls are expected to have corresponding tail notes;
  a head note without a tail note (or vice-versa) is an error.
  StepMania emits a warning and treats disconnected head notes as tap notes
  (and discards orphaned tail notes).

  - :func:`.group_notes` can do the same on an opt-in basis.

* Some properties have legacy aliases, like `FREEZES` in place of `STOPS`.
  Additionally, keysounded SSC charts use a `NOTES2` property for note data
  instead of the usual `NOTES`.
  StepMania looks for these aliases in the absence of the regular property name.

  - Known properties on the :data:`.Simfile` and :data:`.Chart` classes do the same.

* During development of the SSC format,
  timing data on charts ("split timing") was an unstable experimental feature.
  Modern versions of StepMania ignore timing data from these unstable versions
  (prior to version 0.70).

  - :class:`.TimingData` ignores SSC chart timing data from these older versions too.

Even if you don't need the rich functionality of the supplementary modules and
packages, the top-level :mod:`simfile` module and the :class:`.SMSimfile` and
:class:`.SSCSimfile` classes its functions return are thoroughly tested and
offer simple, format-agnostic APIs. While a bespoke regular expression might be
sufficient to parse the majority of simfiles, the **simfile** library is
designed to handle any simfile that StepMania accepts, with escape hatches for
error conditions nearly everywhere an exception can be thrown.
