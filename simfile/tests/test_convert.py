import codecs
import unittest

from ..sm import SMSimfile
from ..ssc import SSCSimfile
from ..convert import *


class TestConvert(unittest.TestCase):
    def test_sm_to_ssc(self):
        with codecs.open('testdata/Robotix.sm', 'r', 'utf-8') as infile:
            sm = SMSimfile(file=infile)
        
        ssc = sm_to_ssc(sm)

        for property, value in sm.items():
            self.assertEqual(value, ssc[property])
        self.assertEqual('0.83', ssc.version)
        self.assertEqual(len(sm.charts), len(ssc.charts))
        for sm_chart, ssc_chart in zip(sm.charts, ssc.charts):
            for property, value in sm_chart.items():
                self.assertEqual(value, ssc_chart[property])
    
    def test_ssc_to_sm_raises_by_default(self):
        with codecs.open('testdata/Springtime.ssc', 'r', 'utf-8') as infile:
            ssc = SSCSimfile(file=infile)
        
        self.assertRaises(InvalidPropertyException, ssc_to_sm, ssc)

    def test_ssc_to_sm_with_lenient_invalid_property_behaviors(self):
        with codecs.open('testdata/Springtime.ssc', 'r', 'utf-8') as infile:
            ssc = SSCSimfile(file=infile)
        
        sm = ssc_to_sm(
            ssc,
            invalid_property_behaviors={
                KnownProperty.GAMEPLAY_EVENT: InvalidPropertyBehavior.IGNORE,
                KnownProperty.TIMING_DATA: InvalidPropertyBehavior.IGNORE,
            },
        )

        for key, value in ssc.items():
            if key == 'VERSION':
                self.assertNotIn(key, sm)
            else:
                self.assertEqual(value, ssc[key])
        self.assertEqual(len(ssc.charts), len(sm.charts))
        for ssc_chart, sm_chart in zip(ssc.charts, sm.charts):
            # We're iterating over the output sm_chart on purpose:
            # SMChart cannot accept fields that it doesn't know about
            for property, value in sm_chart.items():
                self.assertEqual(value, ssc_chart[property])