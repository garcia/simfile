#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals
import codecs
import decimal
import os
import unittest

from simfile import *
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


class TestCharts(unittest.TestCase):
    
    def test_get(self):
        charts = get_simfile('Tribal Style.sm').charts
        chart_sx = charts.get(stepstype='dance-single', difficulty='Challenge')
        self.assertIsInstance(chart_sx, Chart)
        self.assertEqual(chart_sx.meter, 10)
        chart_sh = charts.get(stepstype='dance-single', difficulty='Hard')
        self.assertEqual(chart_sh.meter, 9)
        chart_dx = charts.get(stepstype='dance-double', difficulty='Challenge')
        self.assertEqual(chart_dx.meter, 11)
        chart_dh = charts.get(stepstype='dance-double', difficulty='Hard')
        self.assertEqual(chart_dh.meter, 9)
        chart_sn = charts.get(difficulty='Beginner')
        self.assertEqual(chart_sn.meter, 1)
        self.assertEqual(charts.get(description='J.Casarino'), chart_dx)
        self.assertRaises(LookupError, charts.get, difficulty='Easy')
        self.assertRaises(LookupError, charts.get, meter=9)
        self.assertRaises(LookupError, charts.get, description='K. Ward')
    
    def test_filter(self):
        charts = get_simfile('Tribal Style.sm').charts
        chart_sx = charts.get(stepstype='dance-single', difficulty='Challenge')
        chart_dx = charts.get(stepstype='dance-double', difficulty='Challenge')
        self.assertEqual(
            charts.filter(stepstype='dance-single', difficulty='Challenge'),
            Charts([chart_sx])
        )
        self.assertEqual(
            charts.filter(difficulty='Challenge'),
            Charts([chart_sx, chart_dx])
        )
        self.assertEqual(len(charts.filter(stepstype='dance-single')), 5)
        self.assertEqual(len(charts.filter(stepstype='dance-double')), 4)
        # A filter that matches nothing should return an empty Charts object,
        # as opposed to raising an error
        self.assertFalse(charts.filter(stepstype='dance-triple'))

    def test_unicode(self):
        chart_sn = get_simfile('Tribal Style.sm').charts.get(meter=1)
        expected_str = (
            "#NOTES:\n"
            "     dance-single:\n"
            "     K. Ward:\n"
            "     Beginner:\n"
            "     1:\n"
            "     0.104,0.115,0.045,0.000,0.000:\n"
            "0000\n0000\n0000\n0000\n,\n")
        self.assertEqual(unicode(chart_sn)[:len(expected_str)], expected_str)


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
    
    def test_getitem(self):
        sm = get_simfile('Tribal Style.sm')
        # Basic parameter retrieval
        self.assertIn('TITLE', sm)
        title = sm['TITLE']
        self.assertIsInstance(title, basestring)
        self.assertEqual(title, 'Tribal Style')
        # Charts should reside in sm.charts
        self.assertNotIn('NOTES', sm)
        # Despite being 'weird', BPMS and STOPS are still items of sm
        self.assertIn('BPMS', sm)
        self.assertIn('STOPS', sm)
    
    def test_equality(self):
        # Equality is indirectly tested in other methods, but it has subtleties
        # that need to be specifically tested that don't fit in elsewhere.
        sm = Simfile(string='#TITLE:A;#SUBTITLE:B;')
        sm_whitespace = Simfile(string=' #  TITLE   :\tA\n;#\r\rSUBTITLE:\nB\t\n;')
        sm_order = Simfile(string='#SUBTITLE:B;#TITLE:A;')
        sm_identifier_case = Simfile(string='#Title:A;#subtitle:B;')
        sm_value_case = Simfile(string='#TITLE:a;#SUBTITLE:b;')
        sm_chart = Simfile(string='#TITLE:A;#SUBTITLE:B;#NOTES::::1::;')
        sm_chart_2 = Simfile(string='#TITLE:A;#SUBTITLE:B;#NOTES::::2::;')
        self.assertEqual(sm, sm_whitespace)
        self.assertNotEqual(sm, sm_order)
        self.assertEqual(sm, sm_identifier_case)
        self.assertNotEqual(sm, sm_value_case)
        self.assertNotEqual(sm, sm_chart)
        self.assertNotEqual(sm_chart, sm_chart_2)
    
    def test_unicode(self):
        # Comprehensive test that ensures unicode(simfile) returns a perfect
        # representation of the original simfile. This also serves as a "test"
        # of Simfile.save(), which essentially writes unicode(self) to a file.
        sm1 = get_simfile('Tribal Style.sm')
        sm2 = Simfile(string=unicode(sm1))
        self.assertEqual(sm1, sm2)
    
    # TODO: split these into their own classes, flesh out unit tests more
    
    def test_bpms(self):
        sm = get_simfile('Robotix.sm')
        bpms = sm['BPMS']
        self.assertIsInstance(bpms, Timing)
        self.assertEqual(bpms[0][0], 0)
        self.assertEqual(bpms[0][1], 150)
        self.assertEqual(bpms[1][0], 144)
        self.assertEqual(bpms[1][1], decimal.Decimal('170.001'))

    def test_stops(self):
        sm = get_simfile('Robotix.sm')
        stops = sm['STOPS']
        self.assertIsInstance(stops, Timing)
        self.assertEqual(stops[0][0], 313)
        self.assertEqual(stops[0][1], decimal.Decimal('0.400'))
        self.assertEqual(stops[1][0], 344)
        self.assertEqual(stops[1][1], decimal.Decimal('0.400'))


if __name__ == '__main__':
    unittest.main()