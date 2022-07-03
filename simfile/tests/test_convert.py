from typing import cast
import unittest

import simfile
from ..sm import SMSimfile
from ..ssc import SSCSimfile
from ..convert import *


class TestConvert(unittest.TestCase):
    def test_sm_to_ssc(self):
        sm = simfile.open('testdata/Kryptix/Kryptix.sm')
        assert isinstance(sm, SMSimfile)
        
        ssc = sm_to_ssc(sm)

        for property, value in sm.items():
            self.assertEqual(value, ssc[property])
        self.assertEqual('0.83', ssc.version)
        self.assertEqual(len(sm.charts), len(ssc.charts))
        for sm_chart, ssc_chart in zip(sm.charts, ssc.charts):
            for property, value in sm_chart.items():
                self.assertEqual(value, ssc_chart[property])
    
    def test_ssc_to_sm_raises_by_default(self):
        ssc = simfile.open('testdata/Springtime/Springtime.ssc')
        assert isinstance(ssc, SSCSimfile)
        
        self.assertRaises(InvalidPropertyException, ssc_to_sm, ssc)

    def test_ssc_to_sm_with_lenient_invalid_property_behaviors(self):
        ssc = simfile.open('testdata/Springtime/Springtime.ssc')
        assert isinstance(ssc, SSCSimfile)
        
        sm = ssc_to_sm(
            ssc,
            invalid_property_behaviors={
                PropertyType.GAMEPLAY_EVENT: InvalidPropertyBehavior.IGNORE,
                PropertyType.TIMING_DATA: InvalidPropertyBehavior.IGNORE,
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
    
    def test_sm_to_ssc_with_negative_timing_data(self):
        sm = SMSimfile.blank()
        sm.bpms = '0=60,1=-60,2=60'

        # Temporary - when warp conversion is implemented, this will no longer raise
        self.assertRaises(NotImplementedError, sm_to_ssc, sm)
    
    def test_ssc_to_sm_with_warps(self):
        ssc = SSCSimfile.blank()
        ssc.warps = '0=60,1=-60,2=60'
        # Temporary - when warp conversion is implemented, this will no longer raise
        self.assertRaises(NotImplementedError, ssc_to_sm, ssc)