from decimal import Decimal
import unittest

from .helpers import testing_timing_data, testing_timing_data_with_delays_and_warps
from .. import *
from ..engine import *


class TestTimingEngine(unittest.TestCase):
    def test_init(self):
        timing_data = testing_timing_data()
        engine = TimingEngine(timing_data)
        self.assertEqual(timing_data, engine.timing_data)
    
    def test_bpm_at(self):
        timing_data = testing_timing_data()
        engine = TimingEngine(timing_data)
        self.assertEqual(Decimal('120.000'), engine.bpm_at(Beat(-10000)))
        self.assertEqual(Decimal('120.000'), engine.bpm_at(Beat(0)))
        self.assertEqual(Decimal('120.000'), engine.bpm_at(Beat(1) - Beat.tick()))
        self.assertEqual(Decimal('150.000'), engine.bpm_at(Beat(1)))
        self.assertEqual(Decimal('150.000'), engine.bpm_at(Beat(2) - Beat.tick()))
        self.assertEqual(Decimal('200.000'), engine.bpm_at(Beat(2)))
        self.assertEqual(Decimal('200.000'), engine.bpm_at(Beat(3) - Beat.tick()))
        self.assertEqual(Decimal('300.000'), engine.bpm_at(Beat(3)))
        self.assertEqual(Decimal('300.000'), engine.bpm_at(Beat(10000)))
    
    def test_time_at(self):
        timing_data = testing_timing_data()
        engine = TimingEngine(timing_data)
        self.assertAlmostEqual(-0.491, engine.time_at(Beat(-1)))
        self.assertAlmostEqual(0.009, engine.time_at(Beat(0)))
        self.assertAlmostEqual(0.259, engine.time_at(Beat(0.5)))
        self.assertAlmostEqual(0.509, engine.time_at(Beat(1)))
        self.assertAlmostEqual(0.709, engine.time_at(Beat(1.5)))
        self.assertAlmostEqual(0.909, engine.time_at(Beat(2)))
        self.assertAlmostEqual(1.059, engine.time_at(Beat(2.5)))
        self.assertAlmostEqual(1.565, engine.time_at(Beat(2.5) + Beat.tick()), places=3)
        self.assertAlmostEqual(1.709, engine.time_at(Beat(3)))
        self.assertAlmostEqual(1.813, engine.time_at(Beat(3) + Beat.tick()), places=3)
        self.assertAlmostEqual(2.009, engine.time_at(Beat(4)))
        self.assertAlmostEqual(201.209, engine.time_at(Beat(1000)))
    
    def test_beat_at(self):
        timing_data = testing_timing_data()
        engine = TimingEngine(timing_data)
        self.assertEqual(Beat(-1), engine.beat_at(-0.491))
        self.assertEqual(Beat(0), engine.beat_at(0.009))
        self.assertEqual(Beat(0.5), engine.beat_at(0.259))
        self.assertEqual(Beat(1), engine.beat_at(0.509))
        self.assertEqual(Beat(1.5), engine.beat_at(0.709))
        self.assertEqual(Beat(2), engine.beat_at(0.909))
        self.assertEqual(Beat(2.5), engine.beat_at(1.059))
        self.assertEqual(Beat(2.5), engine.beat_at(1.559))
        self.assertEqual(Beat(2.5) + Beat.tick(), engine.beat_at(1.566))
        self.assertEqual(Beat(3), engine.beat_at(1.709))
        self.assertEqual(Beat(3), engine.beat_at(1.809))
        self.assertEqual(Beat(3) + Beat.tick(), engine.beat_at(1.814))
        self.assertEqual(Beat(4), engine.beat_at(2.009))
        self.assertEqual(Beat(1000), engine.beat_at(201.209))
    
    def test_time_at_with_delays_and_warps(self):
        timing_data = testing_timing_data_with_delays_and_warps()
        engine = TimingEngine(timing_data)

        self.assertEqual(0, engine.time_at(Beat(0)))
        self.assertEqual(0.5, engine.time_at(Beat(1), EventTag.DELAY))
        self.assertEqual(0.75, engine.time_at(Beat(1), EventTag.STOP))
        self.assertEqual(1.25, engine.time_at(Beat(2)))
        self.assertEqual(1.25, engine.time_at(Beat(2.5)))
        self.assertEqual(1.5, engine.time_at(Beat(3), EventTag.DELAY))
        self.assertEqual(2.0, engine.time_at(Beat(3), EventTag.STOP))
        self.assertEqual(2.25, engine.time_at(Beat(3), EventTag.STOP_END))
        self.assertEqual(2.75, engine.time_at(Beat(4), EventTag.STOP))
        self.assertEqual(3.0, engine.time_at(Beat(4), EventTag.STOP_END))
        self.assertEqual(3.0, engine.time_at(Beat(4.5)))
        self.assertEqual(3.25, engine.time_at(Beat(5)))
        self.assertEqual(3.25, engine.time_at(Beat(5.25), EventTag.STOP))
        self.assertEqual(3.5, engine.time_at(Beat(5.25), EventTag.STOP_END))
        self.assertEqual(3.5, engine.time_at(Beat(5.5)))
        self.assertEqual(3.75, engine.time_at(Beat(6)))
        self.assertEqual(3.75, engine.time_at(Beat(6.5), EventTag.STOP))
        self.assertEqual(4.0, engine.time_at(Beat(6.5), EventTag.STOP_END))
        self.assertEqual(4.25, engine.time_at(Beat(7), EventTag.DELAY))
        self.assertEqual(4.5, engine.time_at(Beat(7), EventTag.DELAY_END))
        self.assertEqual(4.5, engine.time_at(Beat(7.5)))
        self.assertEqual(4.75, engine.time_at(Beat(8)))
        self.assertEqual(4.75, engine.time_at(Beat(8.25), EventTag.DELAY))
        self.assertEqual(5.0, engine.time_at(Beat(8.25), EventTag.DELAY_END))
        self.assertEqual(5.0, engine.time_at(Beat(8.5)))
        self.assertEqual(5.25, engine.time_at(Beat(9)))
        self.assertEqual(5.25, engine.time_at(Beat(9.5), EventTag.DELAY))
        self.assertEqual(5.5, engine.time_at(Beat(9.5), EventTag.DELAY_END))
        self.assertEqual(5.75, engine.time_at(Beat(10)))
        self.assertEqual(5.75, engine.time_at(Beat(10.25)))
        self.assertEqual(5.75, engine.time_at(Beat(10.5)))
        self.assertEqual(5.75, engine.time_at(Beat(10.75)))
        self.assertEqual(5.875, engine.time_at(Beat(11)))
        self.assertEqual(5.875, engine.time_at(Beat(11.25)))
        self.assertEqual(5.875, engine.time_at(Beat(11.5)))
        self.assertEqual(5.875, engine.time_at(Beat(11.75)))
        self.assertEqual(6.0, engine.time_at(Beat(12)))
        self.assertEqual(6.0, engine.time_at(Beat(12.25)))
        self.assertEqual(6.0, engine.time_at(Beat(12.5)))
        self.assertEqual(6.0, engine.time_at(Beat(12.75)))
    
    def test_beat_at_with_delays_and_warps(self):
        timing_data = testing_timing_data_with_delays_and_warps()
        engine = TimingEngine(timing_data)

        self.assertEqual(Beat(0), engine.beat_at(0.0))