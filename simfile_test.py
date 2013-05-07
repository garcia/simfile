#!/usr/bin/env python
import decimal
import os
import unittest

from simfile import *

class TestSimfile(unittest.TestCase):
    
    def get_simfile(self, filename):
        return Simfile(os.path.join('testdata', filename))
    
    def test_empty(self):
        sm = self.get_simfile('empty.sm')
        self.assertTrue(sm)
        self.assertFalse(sm.params)
        self.assertRaises(KeyError, sm.get, 'TITLE')
    
    def test_comments(self):
        sm = self.get_simfile('comments.sm')
        self.assertEqual(sm.get('TITLE'), Param(('TITLE', 'Comments')))
        self.assertEqual(sm.get('SUBTITLE'), Param(('SUBTITLE', 'Split into two lines')))
        self.assertEqual(sm.get('ARTIST'), Param(('ARTIST', 'Grant Garcia')))
        self.assertEqual(sm.get_string('TITLE'), 'Comments')
    
    def test_duplicates(self):
        sm = self.get_simfile('duplicates.sm')
        self.assertRaises(MultiInstanceError, sm.get, 'TITLE')
        self.assertRaises(MultiInstanceError, sm.get, 'SUBTITLE')
        self.assertRaises(MultiInstanceError, sm.get, 'subtitle')
    
    def test_multivalue(self):
        sm = self.get_simfile('multivalue.sm')
        self.assertEqual(sm.get('TITLE'), Param(('TITLE', 'One value')))
        self.assertEqual(sm.get('SUBTITLE'), Param(('SUBTITLE', 'First value', 'second value')))
        self.assertEqual(sm.get('ARTIST'), Param(('ARTIST', 'One', 'two', 'three')))
        self.assertEqual(sm.get_string('SUBTITLE'), 'First value:second value')
        self.assertEqual(sm.get_string('ARTIST'), 'One:two:three')
    
    def test_no_semicolon(self):
        sm = self.get_simfile('no semicolon.sm')
        self.assertEqual(sm.get('TITLE'), Param(('TITLE', 'No semicolon')))
        self.assertEqual(sm.get('SUBTITLE'), Param(('SUBTITLE', 'EOF')))
    
    def test_types(self):
        sm = self.get_simfile('Tribal Style.sm')
        self.assertIsInstance(sm.get('TITLE'), Param)
        bpm_param = sm.get('BPMS')
        self.assertIsInstance(bpm_param, Param)
        self.assertIsInstance(bpm_param[1], BPMs)
        chart = sm.get_chart(index=0)
        self.assertIsInstance(chart, Chart)
        self.assertIsInstance(chart.notes, Notes)
    
    def test_bpms(self):
        sm = self.get_simfile('Robotix.sm')
        bpms = sm.get('BPMS')[1]
        self.assertEqual(bpms.bpms[0][0], 0)
        self.assertEqual(bpms.bpms[0][1], 150)
        self.assertEqual(bpms.bpms[1][0], 144)
        self.assertEqual(bpms.bpms[1][1], decimal.Decimal('170.001'))
    
    def test_get_chart(self):
        sm = self.get_simfile('Tribal Style.sm')
        chart_sx = sm.get_chart(stepstype='dance-single', difficulty='Challenge')
        self.assertEqual(chart_sx.meter, 10)
        chart_sh = sm.get_chart(stepstype='dance-single', difficulty='Hard')
        self.assertEqual(chart_sh.meter, 9)
        chart_dx = sm.get_chart(stepstype='dance-double', difficulty='Challenge')
        self.assertEqual(chart_dx.meter, 11)
        chart_dh = sm.get_chart(stepstype='dance-double', difficulty='Hard')
        self.assertEqual(chart_dh.meter, 9)
        sm.get_chart(difficulty='Beginner')
        sm.get_chart(meter=11)
        sm.get_chart(index=0)
        sm.get_chart(index=8)
        sm.get_chart(description='J.Casarino')
        self.assertRaises(MultiInstanceError, sm.get_chart, stepstype='dance-single')
        self.assertRaises(MultiInstanceError, sm.get_chart, difficulty='Challenge')
        self.assertRaises(MultiInstanceError, sm.get_chart, description='M.Emirzian')
        self.assertRaises(IndexError, sm.get_chart, index=9)
        self.assertRaises(IndexError, sm.get_chart, meter=9, index=2)
        self.assertRaises(KeyError, sm.get_chart, meter=100)


if __name__ == '__main__':
    unittest.main()