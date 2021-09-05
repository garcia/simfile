# simfile

A modern simfile parsing & editing library for Python 3.

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

**simfile** is available on PyPI. During the current beta phase, make sure to pass `--pre` to `pip`, otherwise you will fetch the 1.0 release:

```bash
pip3 install --pre simfile
```

Version 2.0 is a substantial departure from the 1.0 release. Read **[Migrating from simfile 1.0 to 2.0](https://simfile.readthedocs.io/en/latest/migrating.html)** for a breakdown of the changes. While 2.0 is currently in beta, no further breaking API changes are anticipated before the official 2.0 release.

## Quickstart

Load simfiles from disk using `simfile.open` or `simfile.load`:

```python
>>> import simfile
>>> springtime = simfile.open('testdata/Springtime.ssc')
>>> springtime
<SSCSimfile: Springtime>
>>> with open('testdata/Kryptix.sm', 'r') as infile:
...     kryptix = simfile.load(infile)
...
>>> kryptix
<SMSimfile: Kryptix>
```

Use lowercase attributes to access most common properties:

```python
>>> springtime.artist
'Kommisar'
>>> springtime.banner
'springbn.png'
>>> springtime.subtitle = '(edited)'
>>> springtime
<SSCSimfile: Springtime (edited)>
```

Alternatively, use uppercase strings to access the underlying dictionary:

```python
>>> springtime['ARTIST']
'Kommisar'
>>> springtime['ARTIST'] is springtime.artist
True
>>> list(springtime.keys())[:7]
['VERSION', 'TITLE', 'SUBTITLE', 'ARTIST', 'TITLETRANSLIT', 'SUBTITLETRANSLIT', 'ARTISTTRANSLIT']
```

Charts are stored in a list under the `.charts` attribute and function similarly to simfile objects:

```python
>>> len(springtime.charts)
9
>>> chart = springtime.charts[0]
>>> chart
<SSCChart: dance-single Challenge 12>
>>> list(chart.keys())[:7]
['CHARTNAME', 'STEPSTYPE', 'DESCRIPTION', 'CHARTSTYLE', 'DIFFICULTY', 'METER', 'RADARVALUES']
```

## Further reading

Full documentation can be found on **[Read the Docs](https://simfile.readthedocs.io/en/latest/)**.
