:mod:`simfile` --- Simfile parser library
=========================================

This module provides a parser for .SM simfiles. It can be used to programmatically manipulate simfiles, charts, and note data.

Members
-------

.. automodule:: simfile
   :members: decimal_to_192nd, decimal_from_192nd, Notes, Chart, Charts, Timing, Simfile

Basic usage
-----------

.. testsetup:: import
    
    import os
    if not hasattr(os, 'changed_dir'):
        os.chdir('..')
        os.changed_dir = True

There are multiple ways to import simfiles. The most common method is to pass a filename:

.. doctest:: import

    >>> from simfile import *
    >>> filename = 'testdata/Tribal Style.sm'
    >>> sim = Simfile(filename)
    >>> sim
    <Simfile: Tribal Style>

Simfiles can also be imported from any file-like object:

.. doctest:: import

    >>> import codecs
    >>> with codecs.open(filename, 'r', encoding='utf-8') as infile:
    ...     sim = Simfile(infile)
    ...
    >>> sim
    <Simfile: Tribal Style>

Simfiles can also be imported from strings containing simfile data using the class method :meth:`from_string`:

.. doctest:: import

    >>> with codecs.open('testdata/Tribal Style.sm', 'r', encoding='utf-8') as infile:
    ...     sim = Simfile.from_string(infile.read())
    ...
    >>> sim
    <Simfile: Tribal Style>

All of the import methods listed above yield equivalent Simfile objects.

.. testsetup:: given_sim
    
    import os
    from simfile import *
    if not hasattr(os, 'changed_dir'):
        os.chdir('..')
        os.changed_dir = True
    sim = Simfile('testdata/Tribal Style.sm')

The simfile's parameters are accessible through a :py:class:`dict`-like interface:

.. doctest:: given_sim

    >>> sim['TITLE']
    u'Tribal Style'
    >>> sim['TITLE'] = 'Robotix'
    >>> sim['TITLE']
    'Robotix'
    >>> del sim['TITLE']
    >>> 'TITLE' in sim
    False

Timing data (specifically, the BPMS and STOPS parameters) can be manipulated through the methods exposed by the :class:`Timing` class:

.. doctest:: given_sim

    >>> bpms = sim['BPMS']
    >>> bpms
    Timing([[Fraction(0, 1), Decimal('140.000')]])
    >>> print bpms
    0.000=140.000
    >>> bpms[0][1] += 40
    >>> print bpms
    0.000=180.000

Charts are stored in a :class:`Charts` object that provides two methods for retrieving charts. The first is :meth:`get`, which gets a single chart or raises :py:exc:`LookupError` if zero or two or more charts match:

.. doctest:: given_sim

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

.. doctest:: given_sim

    >>> expert_charts = sim.charts.filter(difficulty='Challenge')
    >>> expert_charts
    Charts([<Chart: dance-single Challenge 10 (C. Foy)>, <Chart: dance-double Challenge 11 (J.Casarino)>])
    >>> expert_charts[1] == double_expert
    True
    >>> len(sim.charts.filter(meter=100))
    0

Charts can also be retrieved by indexing or iterating over the :class:`Charts` object. Their order in the original simfile is preserved.

.. doctest:: given_sim

    >>> for chart in sim.charts:
    ...  print repr(chart)
    ...
    <Chart: dance-single Hard 9 (K.Ward)>
    <Chart: dance-single Medium 6 (K. Ward)>
    <Chart: dance-single Easy 3 (K. Ward)>
    <Chart: dance-single Challenge 10 (C. Foy)>
    <Chart: dance-single Beginner 1 (K. Ward)>
    <Chart: dance-double Easy 3 (M.Emirzian)>
    <Chart: dance-double Medium 5 (M.Emirzian)>
    <Chart: dance-double Hard 9 (M.Emirzian)>
    <Chart: dance-double Challenge 11 (J.Casarino)>

:class:`Chart` instances expose their metadata through various attributes:

.. doctest:: given_sim

    >>> chart = sim.charts.get(stepstype='dance-double', meter=11)
    >>> print chart.stepstype
    dance-double
    >>> print chart.meter
    11
    >>> print chart.description
    J.Casarino
    >>> print chart.difficulty
    Challenge
    >>> print chart.radar
    0.785,0.695,0.511,0.206,0.893
    >>> chart.notes
    <simfile.simfile.Notes object at 0x...>
    >>> chart.notes[0]
    [Fraction(16, 1), u'02002000']

After modifying a :class:`Simfile`, it can be saved using the :meth:`save` method, which writes it to a given filename or, if no filename is given, to the file from which it was originally read::

    >>> print sim.filename
    testdata/Tribal Style.sm
    >>> sim.save('testdata/Tribal Style (edited).sm') # Writes to testdata/Tribal Style (edited).sm
    >>> sim.save()                                    # Writes to testdata/Tribal Style.sm

Note that simfiles created using :meth:`from_string` require the filename argument to :meth:`save`.

Examples
--------

Copy transliterated fields to their non-transliterated counterparts::

    from simfile import *
    sim = Simfile('My Simfile.sm')
    for field in ('TITLE', 'SUBTITLE', 'ARTIST'):
        fieldtranslit = field + 'TRANSLIT'
        if fieldtranslit in sim and sim[fieldtranslit]:
            sim[field] = sim[fieldtranslit]
    sim.save()

Change the offset of a simfile written for StepMania 5 to match In The Groove's global offset::

    from decimal import Decimal
    from simfile import *
    sim = Simfile('My Simfile.sm')
    sim['OFFSET'] += Decimal('0.009')
    sim.save()

Set the description of every chart in a pack folder::

    import glob
    from simfile import *
    for sim_path in glob.iglob('Pack/*/*.sm'):
        sim = Simfile(sim_path)
        for chart in sim.charts:
            chart.description = 'Edited'
        sim.save()

Remove all charts that aren't dance-single Challenge charts from a pack folder::

    import glob
    from simfile import *
    for sim_path in glob.iglob('Pack/*/*.sm'):
        sim = Simfile(sim_path)
        sim.charts = sim.charts.filter(stepstype='dance-single', difficulty='Challenge')
        sim.save()