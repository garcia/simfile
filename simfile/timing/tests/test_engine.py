from decimal import Decimal
import unittest

from .helpers import testing_simfile
from .. import *
from ..engine import *


class TestTimingEngine(unittest.TestCase):
    def test_init(self):
        sm = testing_simfile()
        timing_data = TimingData.from_simfile(sm)
        timing_converter = TimingEngine(timing_data)
        self.assertEqual(timing_data, timing_converter.timing_data)
    
    def test_bpm_at(self):
        sm = testing_simfile()
        timing_converter = TimingEngine(TimingData.from_simfile(sm))
        self.assertEqual(Decimal('120.000'), timing_converter.bpm_at(Beat(-10000)))
        self.assertEqual(Decimal('120.000'), timing_converter.bpm_at(Beat(0)))
        self.assertEqual(Decimal('120.000'), timing_converter.bpm_at(Beat(1) - Beat.tick()))
        self.assertEqual(Decimal('150.000'), timing_converter.bpm_at(Beat(1)))
        self.assertEqual(Decimal('150.000'), timing_converter.bpm_at(Beat(2) - Beat.tick()))
        self.assertEqual(Decimal('200.000'), timing_converter.bpm_at(Beat(2)))
        self.assertEqual(Decimal('200.000'), timing_converter.bpm_at(Beat(3) - Beat.tick()))
        self.assertEqual(Decimal('300.000'), timing_converter.bpm_at(Beat(3)))
        self.assertEqual(Decimal('300.000'), timing_converter.bpm_at(Beat(10000)))
    
    def test_time_at(self):
        sm = testing_simfile()
        timing_converter = TimingEngine(TimingData.from_simfile(sm))
        self.assertAlmostEqual(-0.491, timing_converter.time_at(Beat(-1)))
        self.assertAlmostEqual(0.009, timing_converter.time_at(Beat(0)))
        self.assertAlmostEqual(0.259, timing_converter.time_at(Beat(0.5)))
        self.assertAlmostEqual(0.509, timing_converter.time_at(Beat(1)))
        self.assertAlmostEqual(0.709, timing_converter.time_at(Beat(1.5)))
        self.assertAlmostEqual(0.909, timing_converter.time_at(Beat(2)))
        self.assertAlmostEqual(1.059, timing_converter.time_at(Beat(2.5)))
        self.assertAlmostEqual(1.565, timing_converter.time_at(Beat(2.5) + Beat.tick()), places=3)
        self.assertAlmostEqual(1.709, timing_converter.time_at(Beat(3)))
        self.assertAlmostEqual(1.813, timing_converter.time_at(Beat(3) + Beat.tick()), places=3)
        self.assertAlmostEqual(2.009, timing_converter.time_at(Beat(4)))
        self.assertAlmostEqual(201.209, timing_converter.time_at(Beat(1000)))
    
    def test_beat_at(self):
        sm = testing_simfile()
        timing_converter = TimingEngine(TimingData.from_simfile(sm))
        self.assertEqual(Beat(-1), timing_converter.beat_at(-0.491))
        self.assertEqual(Beat(0), timing_converter.beat_at(0.009))
        self.assertEqual(Beat(0.5), timing_converter.beat_at(0.259))
        self.assertEqual(Beat(1), timing_converter.beat_at(0.509))
        self.assertEqual(Beat(1.5), timing_converter.beat_at(0.709))
        self.assertEqual(Beat(2), timing_converter.beat_at(0.909))
        self.assertEqual(Beat(2.5), timing_converter.beat_at(1.059))
        self.assertEqual(Beat(2.5), timing_converter.beat_at(1.559))
        self.assertEqual(Beat(2.5) + Beat.tick(), timing_converter.beat_at(1.566))
        self.assertEqual(Beat(3), timing_converter.beat_at(1.709))
        self.assertEqual(Beat(3), timing_converter.beat_at(1.809))
        self.assertEqual(Beat(3) + Beat.tick(), timing_converter.beat_at(1.814))
        self.assertEqual(Beat(4), timing_converter.beat_at(2.009))
        self.assertEqual(Beat(1000), timing_converter.beat_at(201.209))