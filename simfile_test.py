#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals
import codecs
import decimal
import os
import unittest

from simfile import Simfile, Timing
from simfile.msd import MSDParser

def get_parser(filename):
    return MSDParser(codecs.open(os.path.join('testdata', filename), 'r',
        encoding='utf-8'))

def get_simfile(filename):
    return Simfile(os.path.join('testdata', filename))

class TestMSD(unittest.TestCase):
    
    def test_empty(self):
        parser = get_parser('empty.sm')
        # Generator should exist
        self.assertTrue(parser)
        # Generator should yield absolutely nothing
        for param in parser:
            self.fail()
    
    def test_comments(self):
        parser = get_parser('comments.sm')
        self.assertEqual(parser.next(), ['TITLE', 'Comments'])
        self.assertEqual(parser.next(), ['SUBTITLE', 'Split into two lines'])
        self.assertEqual(parser.next(), ['ARTIST', 'Grant/Garcia'])
        self.assertRaises(StopIteration, parser.next)

    def test_duplicates(self):
        parser = get_parser('duplicates.sm')
        self.assertEqual(parser.next(), ['TITLE', 'First duplicate field'])
        self.assertEqual(parser.next(), ['TITLE', 'Second duplicate field'])
        self.assertEqual(parser.next(), ['SUBTITLE', 'CASE INSENSITIVITY'])
        self.assertEqual(parser.next(), ['Subtitle', 'case insensitivity'])
        self.assertRaises(StopIteration, parser.next)

    def test_multivalue(self):
        parser = get_parser('multivalue.sm')
        self.assertEqual(parser.next(), ['TITLE', 'One value'])
        self.assertEqual(parser.next(), ['SUBTITLE', 'First value', 'second value'])
        self.assertEqual(parser.next(), ['ARTIST', 'One', 'two', 'three'])
        self.assertRaises(StopIteration, parser.next)

    def test_no_semicolon(self):
        parser = get_parser('no semicolon.sm')
        self.assertEqual(parser.next(), ['TITLE', 'No semicolon'])
        self.assertEqual(parser.next(), ['SUBTITLE', 'EOF'])
        self.assertRaises(StopIteration, parser.next)

    def test_unicode(self):
        parser = get_parser('unicode.sm')
        self.assertEqual(parser.next(), ['TITLE', '実例'])
        self.assertEqual(parser.next(), ['ARTIST', '楽士'])
        self.assertRaises(StopIteration, parser.next)

class TestSimfile(unittest.TestCase):
    
    def test_init(self):
        # Can't pass both filename and string
        self.assertRaises(TypeError, Simfile, filename='.', string='.')
        sm1 = Simfile('testdata/Tribal Style.sm')
        # Named 'filename' argument can be positionally inferred
        self.assertEqual(sm1, Simfile(filename='testdata/Tribal Style.sm'))
        # Reading file from string should return identical results
        # (except for the filename and dirname properties, but those aren't
        # considered when comparing simfiles)
        with codecs.open('testdata/Tribal Style.sm', 'r', 'utf-8') as sm2:
            self.assertEqual(sm1, Simfile(string=sm2.read()))
    
    def test_types(self):
        sm = get_simfile('Tribal Style.sm')
        self.assertIsInstance(sm['TITLE'], basestring)
        self.assertIsInstance(sm['BPMS'], Timing)
        self.assertIsInstance(sm['STOPS'], Timing)
        #chart = sm.get_chart(index=0)
        #self.assertIsInstance(chart, Chart)
        #self.assertIsInstance(chart.notes, Notes)
    
    def test_getitem(self):
        sm = get_simfile('Tribal Style.sm')
        # Basic parameter retrieval
        self.assertIn('TITLE', sm)
        self.assertEqual(sm['TITLE'], 'Tribal Style')
        # Charts should reside in sm.charts
        self.assertNotIn('NOTES', sm)
        # Despite being 'weird', BPMS and STOPS are still items of sm
        self.assertIn('BPMS', sm)
        self.assertIn('STOPS', sm)

    def test_bpms(self):
        sm = get_simfile('Robotix.sm')
        bpms = sm['BPMS']
        self.assertEqual(bpms[0][0], 0)
        self.assertEqual(bpms[0][1], 150)
        self.assertEqual(bpms[1][0], 144)
        self.assertEqual(bpms[1][1], decimal.Decimal('170.001'))

    def test_stops(self):
        sm = get_simfile('Robotix.sm')
        stops = sm['STOPS']
        self.assertEqual(stops[0][0], 313)
        self.assertEqual(stops[0][1], decimal.Decimal('0.400'))
        self.assertEqual(stops[1][0], 344)
        self.assertEqual(stops[1][1], decimal.Decimal('0.400'))

    """def test_get_chart(self):
        sm = get_simfile('Tribal Style.sm')
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
        sm = get_simfile('Tribal Style.sm')
        self.assertEqual(unicode(sm.get('TITLE')), '#TITLE:Tribal Style;')
        self.assertEqual(unicode(sm.get('Artist')), '#ARTIST:KaW;')
        bpms_param = sm.get('BPMS')
        self.assertEqual(unicode(bpms_param), '#BPMS:0.000=140.000;')
        self.assertEqual(unicode(bpms_param[1]), '0.000=140.000')
        stops_param = sm.get('STOPS')
        self.assertEqual(unicode(stops_param), '#STOPS:;')
        self.assertEqual(unicode(stops_param[1]), '')

    def test_chart_unicode(self):
        sm = get_simfile('Tribal Style.sm')
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
        sm1 = get_simfile('Tribal Style.sm')
        sm2 = Simfile(string=unicode(sm1))
        self.assertEqual(sm1, sm2)
    
    # The following tests hinge on whether the above test passes or not.
    # (Technically they don't -have- to be underneath it, but it feels cleaner
    # this way.)
    
    def test_pop(self):
        sm1 = get_simfile('Tribal Style.sm', clone=True)
        title = sm1.pop('TITLE')
        self.assertEqual(title, Param(('TITLE', 'Tribal Style')))
        self.assertRaises(KeyError, sm1.pop, 'TITLE')
        sm2 = get_simfile('duplicates.sm', clone=True)
        self.assertEqual(sm2.pop('TITLE'), Param(('TITLE', 'First duplicate field')))
        self.assertEqual(sm2.pop('TITLE'), Param(('TITLE', 'Second duplicate field')))
        self.assertRaises(KeyError, sm2.pop, 'TITLE')
        self.assertEqual(sm2.pop('SUBTITLE', index=1), Param(('Subtitle', 'case insensitivity')))
        self.assertRaises(IndexError, sm2.pop, 'SUBTITLE', index=1)
        self.assertEqual(sm2.pop('SUBTITLE'), Param(('SUBTITLE', 'CASE INSENSITIVITY')))
        self.assertRaises(KeyError, sm2.pop, 'SUBTITLE')
    
    def test_pop_chart(self):
        sm = get_simfile('Tribal Style.sm', clone=True)
        chart1 = sm.get_chart(index=0)
        chart2 = sm.pop_chart(index=0)
        self.assertEqual(chart1, chart2)
        chart3 = sm.get_chart(index=0)
        self.assertNotEqual(chart1, chart3)
        chart4 = sm.pop_chart(index=1)
        self.assertNotEqual(chart3, chart4)
    
    def test_set(self):
        sm = Simfile(string='')
        sm.set('PARAM1', 'Value');
        self.assertEqual(sm.get('PARAM1'), Param(('PARAM1', 'Value')))
        self.assertEqual(len([param for param in sm]), 1)
        sm.set('PARAM2', 'Value 1', 'Value 2')
        self.assertEqual(sm.get('PARAM2'), Param(('PARAM2', 'Value 1', 'Value 2')))
        self.assertEqual(len([param for param in sm]), 2)
        sm.set('PARAM1', 'Other value', '')
        self.assertEqual(sm.get('PARAM1'), Param(('PARAM1', 'Other value', '')))
        self.assertEqual(len([param for param in sm]), 2)
        sm.set('PARAM2', '')
        self.assertEqual(sm.get('PARAM2'), Param(('PARAM2', '')))
        self.assertEqual(len([param for param in sm]), 2)
        sm.set('PARAM3')
        self.assertEqual(sm.get('PARAM3'), Param(('PARAM3',)))
        self.assertEqual(len([param for param in sm]), 3)"""


if __name__ == '__main__':
    unittest.main()