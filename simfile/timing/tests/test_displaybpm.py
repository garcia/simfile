from decimal import Decimal
import unittest

from simfile.sm import SMSimfile

from ..displaybpm import *
import simfile


class TestDisplayBPM(unittest.TestCase):
    def test_static_value(self):
        springtime = simfile.open("testdata/Springtime/Springtime.ssc")
        result = displaybpm(springtime)
        self.assertEqual(StaticDisplayBPM(value=Decimal("182")), result)
        self.assertEqual("182", str(result))

    def test_ssc_chart_and_static_value(self):
        springtime = simfile.open("testdata/Springtime/Springtime.ssc")
        result = displaybpm(springtime, springtime.charts[0])
        self.assertEqual(StaticDisplayBPM(value=Decimal("182")), result)
        self.assertEqual("182", str(result))

    def test_range_value(self):
        springtime = simfile.open("testdata/Springtime/Springtime.ssc")
        del springtime["DISPLAYBPM"]
        del springtime.charts[0]["DISPLAYBPM"]
        result = displaybpm(springtime, springtime.charts[0])
        self.assertEqual(
            RangeDisplayBPM(min=Decimal("90.843"), max=Decimal("181.685")),
            result,
        )
        self.assertEqual("91:182", str(result))

    def test_random_value(self):
        springtime = simfile.open("testdata/Springtime/Springtime.ssc")
        springtime.displaybpm = "*"
        result = displaybpm(springtime)
        self.assertEqual(RandomDisplayBPM(), result)
        self.assertEqual("*", str(result))

    def test_empty_value(self):
        sm = SMSimfile.blank()
        sm.bpms = "0=120"
        sm.displaybpm = ""
        result = displaybpm(sm)
        self.assertEqual(StaticDisplayBPM(Decimal(120)), result)

    def test_junk_value(self):
        sm = SMSimfile.blank()
        sm.bpms = "0=120"
        sm.displaybpm = "0=240"
        result = displaybpm(sm)
        self.assertEqual(StaticDisplayBPM(Decimal(120)), result)

    def test_junk_value_and_colon(self):
        sm = SMSimfile.blank()
        sm.bpms = "0=120"
        sm.displaybpm = "0:60:240"
        result = displaybpm(sm)
        self.assertEqual(StaticDisplayBPM(Decimal(120)), result)

    def test_ignore_specified(self):
        springtime = simfile.open("testdata/Springtime/Springtime.ssc")
        result = displaybpm(springtime, springtime.charts[0], ignore_specified=True)
        self.assertEqual(
            RangeDisplayBPM(min=Decimal("90.843"), max=Decimal("181.685")),
            result,
        )
        self.assertEqual("91:182", str(result))


class TestStaticDisplayBPM(unittest.TestCase):
    def test_properties(self):
        sm = SMSimfile.blank()
        sm.bpms = "0=120"
        result = displaybpm(sm)
        self.assertEqual(Decimal(120), result.value)
        self.assertEqual(Decimal(120), result.min)
        self.assertEqual(Decimal(120), result.max)
        self.assertIsNone(result.range)


class TestRangeDisplayBPM(unittest.TestCase):
    def test_properties(self):
        sm = SMSimfile.blank()
        sm.bpms = "0=120,4=240"
        result = displaybpm(sm)
        self.assertIsNone(result.value)
        self.assertEqual(Decimal(120), result.min)
        self.assertEqual(Decimal(240), result.max)
        self.assertEqual((Decimal(120), Decimal(240)), result.range)


class TestRandomDisplayBPM(unittest.TestCase):
    def test_properties(self):
        sm = SMSimfile.blank()
        sm.bpms = "0=120,4=240"
        sm.displaybpm = "*"
        result = displaybpm(sm)
        self.assertIsNone(result.value)
        self.assertIsNone(result.min)
        self.assertIsNone(result.max)
        self.assertIsNone(result.range)
