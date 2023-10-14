![simfile - for Python 3](docs/source/_static/simfile-600.png?raw=true)

A modern simfile parsing & editing library for Python 3.

Full documentation can be found on **[Read the Docs](https://simfile.readthedocs.io/en/latest/)**.

## Features

- Supports both SM and SSC files
  - [Format-agnostic API for reading & writing simfiles](https://simfile.readthedocs.io/en/latest/reading-writing.html)
  - [SM ↔︎ SSC conversion](https://simfile.readthedocs.io/en/latest/autoapi/simfile/convert/index.html)
- [Timing data support](https://simfile.readthedocs.io/en/latest/timing-note-data.html#reading-timing-data)
  - [Beat ↔︎ song time conversion](https://simfile.readthedocs.io/en/latest/timing-note-data.html#converting-song-time-to-beats)
  - Handles BPM changes, stops, delays and warps
  - Accepts "split timing" from SSC charts
- [Note streams from charts](https://simfile.readthedocs.io/en/latest/timing-note-data.html#reading-note-data)
  - [Algorithms for grouping jumps & hold/roll head/tail notes](https://simfile.readthedocs.io/en/latest/timing-note-data.html#handling-holds-rolls-and-jumps)
  - [Flexible note counting functions](https://simfile.readthedocs.io/en/latest/timing-note-data.html#counting-notes)
  - [Timing data integration](https://simfile.readthedocs.io/en/latest/timing-note-data.html#combining-notes-and-time)
- Fully typed, documented, and tested API

## Installation

**simfile** is available on PyPI:

```bash
pip3 install simfile
```

## Quickstart

Load simfiles from disk using `simfile.open` or `simfile.load`:

```python
>>> import simfile
>>> springtime = simfile.open('testdata/Springtime/Springtime.ssc')
>>> springtime
<SSCSimfile: Springtime>
>>> with open('testdata/nekonabe/nekonabe.sm', 'r') as infile:
...     nekonabe = simfile.load(infile)
...
>>> nekonabe
<SMSimfile: 猫鍋>
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

## Developing

**simfile** uses Poetry for dependency management. Activate the environment:

```bash
poetry shell
```

To run the unit tests:

```bash
python3 -m unittest
```

To build the documentation:

```bash
docs/make html
```
