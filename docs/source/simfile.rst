:mod:`simfile` --- Simfile parser library
=========================================

This module provides a parser for .SM simfiles. It can be used to programmatically manipulate simfiles, charts, and note data.

Members
-------

.. automodule:: simfile
   :members: decimal_to_192nd, decimal_from_192nd, Notes, Chart, Charts, Timing, Simfile

Basic usage
-----------

.. testsetup:: *
    
    from os import chdir
    from simfile import *
    chdir("..")
    sim = Simfile("testdata/Tribal Style.sm")

There are two ways to import simfiles. To import a simfile from the filesystem, pass the filename as the sole argument to the constructor::

    >>> from simfile import *
    >>> sim = Simfile("testdata/Tribal Style.sm")
    >>> sim
    <Simfile: Tribal Style>

Alternatively, a string containing simfile data can be imported using the named argument `string`:

.. doctest::

    >>> import codecs
    >>> with codecs.open("testdata/Tribal Style.sm", "r", encoding="utf-8") as infile:
    ...     sim = Simfile(string=infile.read())
    ...
    >>> sim
    <Simfile: Tribal Style>

The simfile's parameters are accessible through a :py:class:`dict`-like interface:

.. doctest::

    >>> sim['TITLE']
    u'Tribal Style'
    >>> sim['TITLE'] = 'Robotix'
    >>> sim['TITLE']
    'Robotix'
    >>> del sim['TITLE']
    >>> 'TITLE' in sim
    False

Timing data (specifically, the BPMS and STOPS parameters) can be manipulated through the methods exposed by the :class:`Timing` class:

.. doctest::

    >>> bpms = sim['BPMS']
    >>> bpms
    Timing([[Fraction(0, 1), Decimal('140.000')]])
    >>> print bpms
    0.000=140.000
    >>> bpms[0][1] += 40
    >>> print bpms
    0.000=180.000

Charts are stored in a :class:`Charts` object that provides two methods for retrieving charts. The first is :meth:`get`, which gets a single chart or raises :py:exc:`LookupError` if zero or two or more charts match:

.. doctest::

    >>> single_novice = sim.charts.get(difficulty='Beginner')
    >>> single_novice
    <Chart: dance-single Beginner 1 (K. Ward)>
    >>> single_novice.meter
    1
    >>> double_expert = sim.charts.get(difficulty='Challenge', stepstype='dance-double')
    >>> double_expert.meter
    11
    >>> sim.charts.get(meter=100)
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    LookupError: 0 charts match the given parameters
    >>> sim.charts.get(stepstype='dance-single')
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    LookupError: 5 charts match the given parameters

The second method is :meth:`filter`, which gets any and all charts that match the query:

.. doctest::

    >>> expert_charts = sim.charts.filter(difficulty='Challenge')
    >>> expert_charts
    Charts([<Chart: dance-single Challenge 10 (C. Foy)>, <Chart: dance-double Challenge 11 (J.Casarino)>])
    >>> expert_charts[1] == double_expert
    True
    >>> len(sim.charts.filter(meter=100))
    0

Charts can also be retrieved directly from the :class:`Charts` object:

.. doctest::

    >>> first_chart = sim.charts[0]
    >>> print first_chart.stepstype, first_chart.difficulty, first_chart.meter
    dance-single Hard 9

In addition to the fields illustrated above, :class:`Chart` instances expose their note data as a :class:`Notes` object:

.. doctest::

    >>> notes = sim.charts.get(stepstype='dance-double', meter=11).notes
    >>> notes
    <simfile.simfile.Notes object at 0x...>
    >>> notes[0]
    [Fraction(16, 1), u'02002000']

Examples
--------

Set the description of every chart::

    from simfile import *
    sim = Simfile("testdata/Tribal Style.sm")
    for chart in sim.charts:
        chart.description = 'Edited'
    sim.save()

If there is a transliterated title available, set it as the primary title::

    from simfile import *
    sim = Simfile("testdata/Tribal Style.sm")
    if 'TITLETRANSLIT' in sim:
        sim['TITLE'] = sim['TITLETRANSLIT']
    except KeyError:
        pass
    sim.save()