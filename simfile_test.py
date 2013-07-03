#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
import os
import unittest

from simfile import *

class TestSimfile(unittest.TestCase):
    
    cache = {}
    
    def get_simfile(self, filename, clone=False):
        if filename not in self.cache:
            self.cache[filename] = Simfile(os.path.join('testdata', filename))
        if clone:
            return Simfile(string=unicode(self.cache[filename]))
        else:
            return self.cache[filename]
    
    def test_empty(self):
        sm = self.get_simfile('empty.sm')
        self.assertTrue(sm)
        self.assertFalse(sm.params)
        self.assertRaises(KeyError, sm.get, 'TITLE')
        # Nowhere else to put these at the moment
        self.assertRaises(TypeError, Simfile, filename='.', string='.')
    
    def test_get(self):
        sm = self.get_simfile('Tribal Style.sm')
        self.assertEqual(sm.get('TITLE'), Param(('TITLE', 'Tribal Style')))
        self.assertRaises(ValueError, sm.get, 'NOTES')
    
    def test_get_string(self):
        sm = self.get_simfile('Tribal Style.sm')
        self.assertEqual(sm.get_string('TITLE'), 'Tribal Style')
        self.assertRaises(ValueError, sm.get_string, 'NOTES')
    
    def test_comments(self):
        sm = self.get_simfile('comments.sm')
        self.assertEqual(sm.get('TITLE'), Param(('TITLE', 'Comments')))
        self.assertEqual(sm.get('SUBTITLE'), Param(('SUBTITLE', 'Split into two lines')))
        self.assertEqual(sm.get('ARTIST'), Param(('ARTIST', 'Grant/Garcia')))
        self.assertEqual(sm.get_string('TITLE'), 'Comments')

    def test_duplicates(self):
        sm = self.get_simfile('duplicates.sm')
        self.assertEqual(sm.get('TITLE'), Param(('TITLE', 'First duplicate field')))
        self.assertEqual(sm.get('TITLE', 1), Param(('TITLE', 'Second duplicate field')))
        self.assertEqual(sm.get('SUBTITLE', 0), Param(('SUBTITLE', 'CASE INSENSITIVITY')))
        self.assertEqual(sm.get('SUBTITLE', 1), Param(('Subtitle', 'case insensitivity')))

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

    def test_unicode(self):
        sm1 = self.get_simfile('unicode.sm')
        sm2 = Simfile(string=unicode(sm1))
        self.assertEqual(sm1.get('TITLE'), Param(('TITLE', u'実例')));
        self.assertEqual(sm1.get('ARTIST'), Param(('ARTIST', u'楽士')));
        self.assertEqual(sm1.get('TITLE'), sm2.get('TITLE'));


    def test_types(self):
        sm = self.get_simfile('Tribal Style.sm')
        self.assertIsInstance(sm.get('TITLE'), Param)
        bpms_param = sm.get('BPMS')
        self.assertIsInstance(bpms_param, Param)
        self.assertIsInstance(bpms_param[1], Timing)
        stops_param = sm.get('STOPS')
        self.assertIsInstance(stops_param[1], Timing)
        chart = sm.get_chart(index=0)
        self.assertIsInstance(chart, Chart)
        self.assertIsInstance(chart.notes, Notes)

    def test_bpms(self):
        sm = self.get_simfile('Robotix.sm')
        bpms = sm.get('BPMS')[1]
        self.assertEqual(bpms[0][0], 0)
        self.assertEqual(bpms[0][1], 150)
        self.assertEqual(bpms[1][0], 144)
        self.assertEqual(bpms[1][1], decimal.Decimal('170.001'))

    def test_stops(self):
        sm = self.get_simfile('Robotix.sm')
        stops = sm.get('STOPS')[1]
        self.assertEqual(stops[0][0], 313)
        self.assertEqual(stops[0][1], decimal.Decimal('0.400'))
        self.assertEqual(stops[1][0], 344)
        self.assertEqual(stops[1][1], decimal.Decimal('0.400'))

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
        self.assertRaises(IndexError, sm.get_chart, index=9)
        self.assertRaises(IndexError, sm.get_chart, meter=9, index=2)
        self.assertRaises(KeyError, sm.get_chart, meter=100)

    def test_param_unicode(self):
        sm = self.get_simfile('Tribal Style.sm')
        self.assertEqual(unicode(sm.get('TITLE')), '#TITLE:Tribal Style;')
        self.assertEqual(unicode(sm.get('Artist')), '#ARTIST:KaW;')
        bpms_param = sm.get('BPMS')
        self.assertEqual(unicode(bpms_param), '#BPMS:0.000=140.000;')
        self.assertEqual(unicode(bpms_param[1]), '0.000=140.000')
        stops_param = sm.get('STOPS')
        self.assertEqual(unicode(stops_param), '#STOPS:;')
        self.assertEqual(unicode(stops_param[1]), '')

    def test_chart_unicode(self):
        sm = self.get_simfile('Tribal Style.sm')
        chart_sn = sm.get_chart(meter=1)
        expected_str = (
            "#NOTES:\n"
            "     dance-single:\n"
            "     K. Ward:\n"
            "     Beginner:\n"
            "     1:\n"
            "     0.104,0.115,0.045,0.000,0.000:\n"
            "0000\n0000\n0000\n0000\n,\n")
        self.assertEqual(unicode(chart_sn)[:len(expected_str)], expected_str)

    def test_simfile_unicode(self):
        # Comprehensive test that ensures unicode(simfile) returns a perfect
        # representation of the original simfile. This also serves as a "test"
        # of Simfile.save(), which essentially writes unicode(self) to a file.
        sm1 = self.get_simfile('Tribal Style.sm')
        sm2 = Simfile(string=unicode(sm1))
        self.assertEqual(sm1, sm2)
    
    # The following tests hinge on whether the above test passes or not.
    # (Technically they don't -have- to be underneath it, but it feels cleaner
    # this way.)
    
    def test_pop(self):
        sm1 = self.get_simfile('Tribal Style.sm', clone=True)
        title = sm1.pop('TITLE')
        self.assertEqual(title, Param(('TITLE', 'Tribal Style')))
        self.assertRaises(KeyError, sm1.pop, 'TITLE')
        sm2 = self.get_simfile('duplicates.sm', clone=True)
        self.assertEqual(sm2.pop('TITLE'), Param(('TITLE', 'First duplicate field')))
        self.assertEqual(sm2.pop('TITLE'), Param(('TITLE', 'Second duplicate field')))
        self.assertRaises(KeyError, sm2.pop, 'TITLE')
        self.assertEqual(sm2.pop('SUBTITLE', index=1), Param(('Subtitle', 'case insensitivity')))
        self.assertRaises(IndexError, sm2.pop, 'SUBTITLE', index=1)
        self.assertEqual(sm2.pop('SUBTITLE'), Param(('SUBTITLE', 'CASE INSENSITIVITY')))
        self.assertRaises(KeyError, sm2.pop, 'SUBTITLE')
    
    def test_pop_chart(self):
        sm = self.get_simfile('Tribal Style.sm', clone=True)
        chart1 = sm.get_chart(index=0)
        chart2 = sm.pop_chart(index=0)
        self.assertEqual(chart1, chart2)
        self.assertNotEqual(chart1, sm.get_chart(index=0))


if __name__ == '__main__':
    unittest.main()
