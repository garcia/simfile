.. image:: _static/simfile-no-outline.svg
  :width: 450
  :alt: simfile - for Python 3

simfile - Modern simfile library for Python
===========================================

A modern simfile parsing & editing library for Python 3.

Installation
------------

**simfile** is available on PyPI:

.. code-block:: bash

   pip3 install simfile

Quickstart
----------

Load simfiles from disk using :func:`simfile.open` or :func:`simfile.load`:

.. doctest::

   >>> import simfile
   >>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
   >>> springtime
   <SSCSimfile: Springtime>
   >>> with open('testdata/nekonabe/nekonabe.sm', 'r') as infile:
   ...     nekonabe = simfile.load(infile)
   ...
   >>> nekonabe
   <SMSimfile: 猫鍋>

Use lowercase attributes to access most common properties:

   >>> springtime.artist
   'Kommisar'
   >>> springtime.banner
   'springbn.png'
   >>> springtime.subtitle = '(edited)'
   >>> springtime
   <SSCSimfile: Springtime (edited)>

Alternatively, use uppercase strings to access the underlying dictionary:

   >>> springtime['ARTIST']
   'Kommisar'
   >>> springtime['ARTIST'] is springtime.artist
   True
   >>> list(springtime.keys())[:7]
   ['VERSION', 'TITLE', 'SUBTITLE', 'ARTIST', 'TITLETRANSLIT', 'SUBTITLETRANSLIT', 'ARTISTTRANSLIT']

Charts are stored in a list under the :code:`.charts` attribute and function similarly to simfile objects:

   >>> len(springtime.charts)
   9
   >>> chart = springtime.charts[0]
   >>> chart
   <SSCChart: dance-single Challenge 12>
   >>> chart.stepstype
   'dance-single'
   >>> list(chart.keys())[:7]
   ['CHARTNAME', 'STEPSTYPE', 'DESCRIPTION', 'CHARTSTYLE', 'DIFFICULTY', 'METER', 'RADARVALUES']

Further reading
---------------

.. toctree::
   :maxdepth: 1

   about-simfiles
   reading-writing
   known-properties
   timing-note-data
   changelog
   migrating


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
