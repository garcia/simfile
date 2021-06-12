.. _about-simfiles:

What are simfiles?
==================

Simfiles are how StepMania gameplay content is distributed. The word "simfile"
can refer to the directory containing the song and the .sm or .ssc file (along
with any graphics or other supplementary files), or the .sm or .ssc file
itself. For the purpose of this documentation, we'll call the SM or SSC file
the "simfile" and its folder the "simfile directory".

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

While the file format shown above seems simple (and indeed is), simfiles on the
Internet vary greatly in formatting and data quality. For example:

* Not all simfiles are encoded in UTF-8.
* Not all simfiles contain an `OFFSET` property.
* Not all simfiles are valid MSD documents.
* Not all simfiles containing holds have a 1:1 correspondence between head
  notes to tail notes.
* Not all SSC simfiles use the `NOTES` property (those with keysounds use a
  separate `NOTES2` property).
* Not all SSC simfiles that appear to contain split timing will have it be used
  by StepMania.

This library offers ways to handle all of these caveats and edge cases, either
as an option or by default, depending on the context. Regarding the above
examples:

* :func:`simfile.open` and related functions try each of the four encodings
  supported by StepMania before throwing a :code:`UnicodeDecodeError`.
  :func:`simfile.mutate` additionally preserves the encoding when writing the
  simfile back to the disk.
* :class:`.TimingData` defaults the offset to zero when it's missing from the
  simfile.
* :func:`simfile.open` and related functions accept a `strict` parameter that
  can be set to False to ignore stray text during parsing.
* :func:`.group_notes` accepts parameters that determine how to handle orphaned
  head or tail notes.
* :class:`.NoteData` will automatically read from and write to the correct SSC
  field, whether `NOTES` or `NOTES2`.
* :class:`.TimingData` will ignore split timing from SSC files with a version
  lower than 0.70, the version at which StepMania considers timing data to have
  been truly implemented. (Some older SSC files contain malformed split timing
  data from when the format was in development; StepMania ignores it, so this
  library does too.)

Even if you don't need the rich functionality of the supplementary modules and
packages, the top-level :mod:`simfile` module and the :class:`.SMSimfile` and
:class:`.SSCSimfile` classes its functions return are thoroughly tested and
offer simple, format-agnostic APIs. While a bespoke regular expression might be
sufficient to parse the majority of simfiles, the **simfile** library is
designed to handle any simfile that StepMania accepts, with escape hatches for
error conditions nearly everywhere an exception can be thrown.
