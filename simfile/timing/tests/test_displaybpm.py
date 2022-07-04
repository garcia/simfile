from decimal import Decimal
import unittest

from ..displaybpm import *
import simfile

class TestDisplayBPM(unittest.TestCase):
    def test_displaybpm_with_static_value(self):
        springtime = simfile.open('testdata/Springtime/Springtime.ssc')
        result = displaybpm(springtime)
        self.assertEqual(StaticDisplayBPM(value=Decimal('182')), result)
        self.assertEqual('182', str(result))
    
    def test_displaybpm_with_ssc_chart_and_static_value(self):
        springtime = simfile.open('testdata/Springtime/Springtime.ssc')
        result = displaybpm(springtime, springtime.charts[0])
        self.assertEqual(StaticDisplayBPM(value=Decimal('182')), result)
        self.assertEqual('182', str(result))
    
    def test_displaybpm_with_range_value(self):
        springtime = simfile.open('testdata/Springtime/Springtime.ssc')
        del springtime['DISPLAYBPM']
        del springtime.charts[0]['DISPLAYBPM']
        result = displaybpm(springtime, springtime.charts[0])
        self.assertEqual(
            RangeDisplayBPM(min=Decimal('90.843'), max=Decimal('181.685')),
            result,
        )
        self.assertEqual('91:182', str(result))
    
    def test_displaybpm_with_random_value(self):
        springtime = simfile.open('testdata/Springtime/Springtime.ssc')
        springtime.displaybpm = '*'
        result = displaybpm(springtime)
        self.assertEqual(RandomDisplayBPM(), result)
        self.assertEqual('*', str(result))