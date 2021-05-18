# simfile

A modern simfile parsing & editing library for Python 3.

Version 2.0 is a substantial departure from the 1.0 release. Read **[Migrating from simfile 1.0 to 2.0](https://simfile.readthedocs.io/en/latest/migrating.html)** for a breakdown of the changes. While 2.0 is currently in beta, no further breaking API changes are anticipated before the official 2.0 release.

## Features

* Supports both SM and SSC files
  - Format-agnostic API for reading & writing simfiles
  - SM ↔︎ SSC conversion
* Timing data support
  - Beat ↔︎ song time conversion
  - Handles BPM changes, stops, delays and warps
  - Accepts "split timing" from SSC charts
* Note streams from charts
  - Algorithms for grouping jumps & hold/roll head/tail notes
  - Flexible note counting functions
  - Timing data integration
* Fully typed & documented API

## Installation

`simfile` is available on PyPI. During the current beta phase, make sure to pass `--pre` to `pip`, otherwise you will fetch the 1.0 release:

    pip3 install --pre simfile

## Quickstart

Load simfiles from disk using `simfile.open` or `simfile.load`:

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

Charts are stored in a list under the `.charts` attribute and function similarly to simfile objects:

    >>> len(springtime.charts)
    9
    >>> chart = springtime.charts[0]
    >>> chart
    <SSCChart: dance-single Challenge 12>
    >>> list(chart.keys())[:7]
    ['CHARTNAME', 'STEPSTYPE', 'DESCRIPTION', 'CHARTSTYLE', 'DIFFICULTY', 'METER', 'RADARVALUES']

## Documentation

Full documentation can be found on **[Read the Docs](https://simfile.readthedocs.io/en/latest/)**.
