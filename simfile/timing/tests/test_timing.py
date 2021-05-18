from decimal import Decimal
from simfile.ssc import SSCSimfile
import unittest

from .helpers import testing_simfile
from .. import *
from simfile.sm import SMSimfile

class TestBeat(unittest.TestCase):
    def test_from_str(self):
        self.assertEqual(Beat(0, 1), Beat.from_str('0.000'))
        self.assertEqual(Beat(12*3+1, 3), Beat.from_str('12.333'))
        self.assertEqual(Beat(4, 192), Beat.from_str('0.021'))
        self.assertEqual(Beat(4, 64), Beat.from_str('0.062'))
        self.assertEqual(Beat(4, 48), Beat.from_str('0.083'))
        self.assertEqual(Beat(4, 32), Beat.from_str('0.125'))
        self.assertEqual(Beat(4, 24), Beat.from_str('0.167'))
        self.assertEqual(Beat(4, 16), Beat.from_str('0.250'))
        self.assertEqual(Beat(4, 12), Beat.from_str('0.333'))
        self.assertEqual(Beat(4, 8), Beat.from_str('0.500'))
    
    def test_str(self):
        self.assertEqual('0.000', str(Beat(0, 1)))
        self.assertEqual('12.333', str(Beat(37, 3)))
        self.assertEqual('0.021', str(Beat(4, 192)))
        self.assertEqual('0.062', str(Beat(4, 64)))
        self.assertEqual('0.083', str(Beat(4, 48)))
        self.assertEqual('0.125', str(Beat(4, 32)))
        self.assertEqual('0.167', str(Beat(4, 24)))
        self.assertEqual('0.250', str(Beat(4, 16)))
        self.assertEqual('0.333', str(Beat(4, 12)))
        self.assertEqual('0.500', str(Beat(4, 8)))


class TestBeatValues(unittest.TestCase):
    def test_from_str(self):
        events = BeatValues.from_str('0.000=128.000,\n132.000=64.000,\n147.500=128.000')
        self.assertIsInstance(events[0].beat, Beat)
        self.assertIsInstance(events[0].value, Decimal)
        self.assertEqual(BeatValue(beat=Beat(0, 1), value=Decimal('128.000')), events[0])
        self.assertEqual(BeatValue(beat=Beat(132, 1), value=Decimal('64.000')), events[1])
        self.assertEqual(BeatValue(beat=Beat(147*2+1, 2), value=Decimal('128.000')), events[2])

    def test_serialize(self):
        events = BeatValues.from_str('0.000=128.000,\n132.000=64.000,\n147.500=128.000')
        self.assertEqual('0.000=128.000,\n132.000=64.000,\n147.500=128.000', events.serialize())


class TestTimingData(unittest.TestCase):
    def test_from_simfile(self):
        sm = testing_simfile()
        timing_data = TimingData.from_simfile(sm)
        self.assertEqual(BeatValues.from_str(sm.bpms), timing_data.bpms)
        self.assertEqual(BeatValues.from_str(sm.stops), timing_data.stops)
        self.assertEqual(BeatValues(), timing_data.warps)
        self.assertEqual(Decimal(sm.offset), timing_data.offset)
    
    def test_from_simfile_with_ssc_chart_without_distinct_timing_data(self):
        with open('testdata/Springtime.ssc', 'r', encoding='utf-8') as infile:
            ssc = SSCSimfile(file=infile)
        ssc_chart = next(filter(
            lambda c: c.stepstype == 'pump-single' and c.difficulty == 'Hard',
            ssc.charts
        ))
        timing_data = TimingData.from_simfile(ssc, ssc_chart)
        self.assertEqual(BeatValues.from_str(ssc.bpms), timing_data.bpms)
        self.assertEqual(BeatValues.from_str(ssc.stops), timing_data.stops)
        self.assertEqual(BeatValues(), timing_data.warps)
        self.assertEqual(Decimal(ssc.offset), timing_data.offset)
    
    def test_from_simfile_with_ssc_chart_with_distinct_timing_data(self):
        with open('testdata/Springtime.ssc', 'r', encoding='utf-8') as infile:
            ssc = SSCSimfile(file=infile)
        ssc_chart = next(filter(
            lambda c: c.stepstype == 'pump-single'
                and c.difficulty == 'Challenge',
            ssc.charts
        ))
        timing_data = TimingData.from_simfile(ssc, ssc_chart)
        self.assertEqual(BeatValues.from_str(ssc_chart['BPMS']), timing_data.bpms)
        self.assertEqual(BeatValues.from_str(ssc_chart['STOPS']), timing_data.stops)
        self.assertEqual(BeatValues(), timing_data.warps)
        self.assertEqual(Decimal(ssc_chart['OFFSET']), timing_data.offset)


