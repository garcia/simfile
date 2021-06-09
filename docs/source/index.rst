simfile - Modern simfile library for Python
===========================================

A modern simfile parsing & editing library for Python 3.

Installation
------------

**simfile** is available on PyPI. During the current beta phase, make sure
to pass :code:`--pre` to :code:`pip`, otherwise you will fetch the 1.0 release:

.. code-block:: bash

   pip3 install --pre simfile

Version 2.0 is a substantial departure from the 1.0 release. Read
:ref:`migrating` for a breakdown of the changes. While 2.0 is currently in
beta, no further breaking API changes are anticipated before the official 2.0
release.

Quickstart
----------

Load simfiles from disk using :func:`simfile.open` or :func:`simfile.load`:

.. doctest::

   >>> import simfile
   >>> springtime = simfile.open('testdata/Springtime.ssc')
   >>> springtime
   <SSCSimfile: Springtime>
   >>> with open('testdata/Robotix.sm', 'r') as infile:
   ...     robotix = simfile.load(infile)
   ...
   >>> robotix
   <SMSimfile: Robotix>

Access simfile properties through uppercase keys:

   >>> springtime['ARTIST']
   'Kommisar'
   >>> list(springtime.keys())[:7]
   ['VERSION', 'TITLE', 'SUBTITLE', 'ARTIST', 'TITLETRANSLIT', 'SUBTITLETRANSLIT', 'ARTISTTRANSLIT']

Alternatively, you can use lowercase attributes for known properties:

   >>> robotix.displaybpm
   '150.000'
   >>> robotix.displaybpm is robotix['DISPLAYBPM']
   True

Charts are stored in a list under the :attr:`.charts` attribute and function similarly to simfile objects:

   >>> len(springtime.charts)
   9
   >>> chart = springtime.charts[0]
   >>> chart
   <SSCChart: dance-single Challenge 12>
   >>> list(chart.keys())[:7]
   ['CHARTNAME', 'STEPSTYPE', 'DESCRIPTION', 'CHARTSTYLE', 'DIFFICULTY', 'METER', 'RADARVALUES']

Contents
--------

.. toctree::
   :maxdepth: 1

   reading-writing
   timing-note-data
   changelog
   migrating


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
