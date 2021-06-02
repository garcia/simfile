from decimal import Decimal
import unittest

import simfile
from .helpers import testing_timing_data
from .. import *

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
    
    def test_repr(self):
        self.assertEqual('Beat(0)', repr(Beat(0, 1)))
        self.assertEqual('Beat(12.333)', repr(Beat(37, 3)))
        self.assertEqual('Beat(0.25)', repr(Beat(4, 16)))
        self.assertEqual('Beat(0.333)', repr(Beat(4, 12)))
        self.assertEqual('Beat(0.5)', repr(Beat(4, 8)))
        self.assertEqual('Beat(1, 1000)', repr(Beat(1, 1000)))
    
    def test_fraction_overrides(self):
        a = Beat(5, 3)
        b = 2

        self.assertEqual((0, Beat(5, 3)), divmod(a, b))
        self.assertIsInstance(divmod(a, b)[1], Beat)
        self.assertEqual((1, Beat(1, 3)), divmod(b, a))
        self.assertIsInstance(divmod(b, a)[1], Beat)

        pairs = [
            (Beat(5, 3), abs(a)),       # __abs__
            (Beat(11, 3), a + b),       # __add__
            (Beat(5, 3), a % b),        # __mod__
            (Beat(10, 3), a * b),       # __mul__
            (Beat(-5, 3), -a),          # __neg__
            (Beat(5, 3), +a),           # __pos__
            (Beat(25, 9), a ** b),      # __pow__
            (Beat(11, 3), b + a),       # __radd__
            (Beat(1, 3), b % a),        # __rmod__
            (Beat(10, 3), b * a),       # __rmul__
            (Beat(4, 1), b ** Beat(2)), # __rpow__
            (Beat(1, 3), b - a),        # __rsub__
            (Beat(6, 5), b / a),        # __rtruediv__
            (Beat(-1, 3), a - b),       # __sub__
            (Beat(5, 6), a / b),        # __truediv__
        ]

        for i, (expected, actual) in enumerate(pairs):
            with self.subTest(i=i):
                self.assertEqual(expected, actual)
                self.assertIsInstance(actual, Beat)


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
        self.assertEqual('0.000=128.000,\n132.000=64.000,\n147.500=128.000', str(events))


class TestTimingData(unittest.TestCase):
    def test_attributes(self):
        timing_data = testing_timing_data()
        self.assertEqual(BeatValues([
            BeatValue(beat=Beat(0), value=Decimal('120.000')),
            BeatValue(beat=Beat(1), value=Decimal('150.000')),
            BeatValue(beat=Beat(2), value=Decimal('200.000')),
            BeatValue(beat=Beat(3), value=Decimal('300.000')),
        ]), timing_data.bpms)
        self.assertEqual(BeatValues([
            BeatValue(beat=Beat(2.5), value=Decimal('0.500')),
            BeatValue(beat=Beat(3), value=Decimal('0.100')),
        ]), timing_data.stops)
        self.assertEqual(BeatValues(), timing_data.delays)
        self.assertEqual(BeatValues(), timing_data.warps)
        self.assertEqual(Decimal('-0.009'), timing_data.offset)
    
    def test_from_simfile_with_ssc_chart_without_distinct_timing_data(self):
        ssc = simfile.open('testdata/Springtime.ssc')
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
        ssc = simfile.open('testdata/Springtime.ssc')
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
    
    def test_from_simfile_with_ssc_chart_but_too_old_version(self):
        ssc = simfile.open('testdata/Springtime.ssc')
        ssc.version = '0.69'
        ssc_chart = next(filter(
            lambda c: c.stepstype == 'pump-single'
                and c.difficulty == 'Challenge',
            ssc.charts
        ))
        timing_data = TimingData.from_simfile(ssc, ssc_chart)
        self.assertEqual(BeatValues.from_str(ssc.bpms), timing_data.bpms)
        self.assertEqual(BeatValues.from_str(ssc.stops), timing_data.stops)

    def test_handles_omitted_offset(self):
        sm = simfile.open('testdata/Robotix.sm')
        del sm['OFFSET']
        timing_data = TimingData.from_simfile(sm)
        self.assertEqual(Decimal(0), timing_data.offset)
