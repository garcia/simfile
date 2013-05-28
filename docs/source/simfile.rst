:mod:`simfile` --- Simfile parser library
=========================================

.. automodule:: simfile
   :members:

Basic usage
-----------

There are two ways to import simfiles. To import a simfile from the filesystem, pass the filename as the sole argument to the constructor::

    >>> from simfile import *
    >>> sim = Simfile("testdata/Tribal Style.sm")
    >>> sim
    <simfile.Simfile object at 0x...>

Alternatively, a string containing simfile data can be imported using the named argument `string`::

    >>> with open("testdata/Tribal Style.sm", "r") as infile:
    ...     sim = Simfile(string=infile.read())
    ...
    >>> sim
    <simfile.Simfile object at 0x...>

There are two methods for retrieving the simfile's parameters: :meth:`~Simfile.get` and :meth:`~Simfile.get_string`. The former returns a :class:`Param` containing the entire parameter; the latter returns a string containing only the values following the identifier::

    >>> sim.get('title')
    Param(['TITLE', 'Tribal Style'])
    >>> print _
    #TITLE:Tribal Style;
    >>> sim.get_string('title')
    'Tribal Style'

Since :class:`Param` instances are mutable, they can be used to manipulate the simfile's contents, although this is not the only means of doing so. The methods :meth:`~Simfile.pop`, :meth:`~Simfile.pop_string`, and :meth:`~Simfile.set` can also be used to modify :class:`Simfile` instances::

    >>> title = sim.get('title')
    >>> title[1] = 'Robotix'
    >>> print sim.get('title')
    #TITLE:Robotix;
    >>> sim.set('title', 'Soapy Bubble')
    >>> print sim.pop('title')
    #TITLE:Soapy Bubble;
    >>> try:
    ...     sim.get('title')
    >>> except KeyError:
            print 'KeyError'
    ...
    KeyError

Timing data (specifically, the BPMS and STOPS parameters) can be accessed and manipulated through the methods exposed by the :class:`Timing` class::

    >>> bpms = sim.get('bpms')[1]
    >>> bpms
    Timing([[Fraction(0, 1), Decimal('140.000')]])
    >>> print bpms
    0.000=140.000
    >>> bpms[0][1] += 40
    >>> print bpms
    0.000=180.000

Charts are retrieved and manipulated using the :meth:`~Simfile.get_chart` and :meth:`~Simfile.set_chart` methods, respectively::

    >>> single_novice = sim.get_chart(difficulty='Beginner')
    >>> single_novice
    <simfile.Chart object at 0x...>
    >>> single_novice.meter
    1
    >>> double_expert = sim.get_chart(difficulty='Challenge', stepstype='dance-double')
    >>> double_expert.meter
    11
    >>> first_chart = sim.get_chart(index=0)
    >>> print first_chart.stepstype, first_chart.difficulty, first_chart.meter
    dance-single Hard 9

:class:`Chart` instances also expose the note data as a :class:`Notes` object::

    >>> notes = double_expert.notes
    >>> notes
    <simfile.Notes object at 0x...>
    >>> notes.get_region(16, 20)
    <simfile.Notes object at 0x...>
    >>> print _
    02002000
    00000000
    00100000
    10000000
    00100000
    00000000
    10000000
    00100000
    >>> notes.get_row_string(16)
    '02002000'

Examples
--------

Set the description of every chart::

    from simfile import *
    sim = Simfile("testdata/Tribal Style.sm")
    for chart in filter(lambda p: type(p) is Chart, sim):
        chart.description = 'Edited'
    sim.save()

If there is a transliterated title available, set it as the primary title::

    from simfile import *
    sim = Simfile("testdata/Tribal Style.sm")
    try:
        translit = sim.get_string('TITLETRANSLIT')
        sim.set('TITLE', translit)
    except KeyError:
        pass
    sim.save()