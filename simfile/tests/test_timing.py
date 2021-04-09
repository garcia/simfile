from decimal import Decimal
from fractions import Fraction
import unittest

from ..timing import *
from ..sm import SMSimfile


def testing_simfile():
    return SMSimfile(string=
        '#BPMS:0.000=120.000,\n'
        '1.000=150.000,\n'
        '2.000=200.000,\n'
        '3.000=300.000;\n'
        '#STOPS:2.500=0.500,\n'
        '3.000=0.100;\n'
        '#OFFSET:-0.009;\n'
    )


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


class TestBeatEvents(unittest.TestCase):
    def test_from_str(self):
        events = BeatEvents.from_str('0.000=128.000,\n132.000=64.000,\n147.500=128.000')
        self.assertIsInstance(events[0].beat, Beat)
        self.assertIsInstance(events[0].value, Decimal)
        self.assertEqual(BeatEvent(beat=Beat(0, 1), value=Decimal('128.000')), events[0])
        self.assertEqual(BeatEvent(beat=Beat(132, 1), value=Decimal('64.000')), events[1])
        self.assertEqual(BeatEvent(beat=Beat(147*2+1, 2), value=Decimal('128.000')), events[2])

    def test_serialize(self):
        events = BeatEvents.from_str('0.000=128.000,\n132.000=64.000,\n147.500=128.000')
        self.assertEqual('0.000=128.000,\n132.000=64.000,\n147.500=128.000', events.serialize())


class TestSimfileTiming(unittest.TestCase):
    def test_init(self):
        sm = testing_simfile()
        simfile_timing = SimfileTiming(sm)
        self.assertEqual(BeatEvents.from_str(sm.bpms), simfile_timing.bpms)
        self.assertEqual(BeatEvents.from_str(sm.stops), simfile_timing.stops)
        self.assertEqual(Decimal(sm.offset), simfile_timing.offset)
    
    def test_bpm_at(self):
        sm = testing_simfile()
        simfile_timing = SimfileTiming(sm)
        self.assertEqual(Decimal('120.000'), simfile_timing.bpm_at(Beat(-10000)))
        self.assertEqual(Decimal('120.000'), simfile_timing.bpm_at(Beat(0)))
        self.assertEqual(Decimal('120.000'), simfile_timing.bpm_at(Beat(1) - Beat.tick()))
        self.assertEqual(Decimal('150.000'), simfile_timing.bpm_at(Beat(1)))
        self.assertEqual(Decimal('150.000'), simfile_timing.bpm_at(Beat(2) - Beat.tick()))
        self.assertEqual(Decimal('200.000'), simfile_timing.bpm_at(Beat(2)))
        self.assertEqual(Decimal('200.000'), simfile_timing.bpm_at(Beat(3) - Beat.tick()))
        self.assertEqual(Decimal('300.000'), simfile_timing.bpm_at(Beat(3)))
        self.assertEqual(Decimal('300.000'), simfile_timing.bpm_at(Beat(10000)))
    
    def test_time_at(self):
        sm = testing_simfile()
        simfile_timing = SimfileTiming(sm)
        self.assertAlmostEqual(-0.491, simfile_timing.time_at(Beat(-1)))
        self.assertAlmostEqual(0.009, simfile_timing.time_at(Beat(0)))
        self.assertAlmostEqual(0.259, simfile_timing.time_at(Beat(0.5)))
        self.assertAlmostEqual(0.509, simfile_timing.time_at(Beat(1)))
        self.assertAlmostEqual(0.709, simfile_timing.time_at(Beat(1.5)))
        self.assertAlmostEqual(0.909, simfile_timing.time_at(Beat(2)))
        self.assertAlmostEqual(1.059, simfile_timing.time_at(Beat(2.5)))
        self.assertAlmostEqual(1.565, simfile_timing.time_at(Beat(2.5) + Beat.tick()), places=3)
        self.assertAlmostEqual(1.709, simfile_timing.time_at(Beat(3)))
        self.assertAlmostEqual(1.813, simfile_timing.time_at(Beat(3) + Beat.tick()), places=3)
        self.assertAlmostEqual(2.009, simfile_timing.time_at(Beat(4)))
        self.assertAlmostEqual(201.209, simfile_timing.time_at(Beat(1000)))
    
    def test_beat_at(self):
        sm = testing_simfile()
        simfile_timing = SimfileTiming(sm)
        self.assertEqual(Beat(-1), simfile_timing.beat_at(-0.491))
        self.assertEqual(Beat(0), simfile_timing.beat_at(0.009))
        self.assertEqual(Beat(0.5), simfile_timing.beat_at(0.259))
        self.assertEqual(Beat(1), simfile_timing.beat_at(0.509))
        self.assertEqual(Beat(1.5), simfile_timing.beat_at(0.709))
        self.assertEqual(Beat(2), simfile_timing.beat_at(0.909))
        self.assertEqual(Beat(2.5), simfile_timing.beat_at(1.059))
        self.assertEqual(Beat(2.5), simfile_timing.beat_at(1.565))
        self.assertEqual(Beat(2.5) + Beat.tick(), simfile_timing.beat_at(1.566))
        self.assertEqual(Beat(3), simfile_timing.beat_at(1.709))
        self.assertEqual(Beat(3), simfile_timing.beat_at(1.813))
        self.assertEqual(Beat(3) + Beat.tick(), simfile_timing.beat_at(1.814))
        self.assertEqual(Beat(4), simfile_timing.beat_at(2.009))
        self.assertEqual(Beat(1000), simfile_timing.beat_at(201.209))