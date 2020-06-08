#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals
import codecs
import decimal
from fractions import Fraction
import os
import unittest

from simfile.common import Timing
from simfile.sm import *
from simfile.msd import MSDParser


def get_parser(filename):
    return MSDParser(codecs.open(os.path.join('testdata', filename), 'r',
                     encoding='utf-8'))


def get_simfile(filename, cache={}):
    if not filename in cache:
        with open(os.path.join('testdata', filename), 'r', encoding='utf-8') as infile:
            cache[filename] = SMSimfile(infile)
    return cache[filename]


def get_default_chart():
    return SMChart(msd=iter([[
        'NOTES',
        'dance-single',
        'Ash Garcia',
        'Challenge',
        '12',
        'radar',
        '0000']]))


class TestMSD(unittest.TestCase):

    def test_empty(self):
        with get_parser('empty.sm') as parser:
            # Generator should exist
            self.assertTrue(parser)
            # Generator should yield absolutely nothing
            for param in parser:
                self.fail()

    def test_comments(self):
        expected = [
            ['TITLE', 'Comments'],
            ['SUBTITLE', 'Split into two lines'],
            ['ARTIST', 'Ash/Garcia'],
        ]
        with get_parser('comments.sm') as parser:
            for i, param in enumerate(parser):
                self.assertEqual(param, expected[i])
            self.assertEqual(i + 1, len(expected))

    def test_duplicates(self):
        expected = [
            ['TITLE', 'First duplicate field'],
            ['TITLE', 'Second duplicate field'],
            ['SUBTITLE', 'CASE INSENSITIVITY'],
            ['Subtitle', 'case insensitivity'],
        ]
        with get_parser('duplicates.sm') as parser:
            for i, param in enumerate(parser):
                self.assertEqual(param, expected[i])
            self.assertEqual(i + 1, len(expected))

    def test_multivalue(self):
        expected = [
            ['TITLE', 'One value'],
            ['SUBTITLE', 'First value', 'second value'],
            ['ARTIST', 'One', 'two', 'three'],
        ]
        with get_parser('multivalue.sm') as parser:
            for i, param in enumerate(parser):
                self.assertEqual(param, expected[i])
            self.assertEqual(i + 1, len(expected))

    def test_no_semicolon(self):
        expected = [
            ['TITLE', 'No semicolon\n'],
            ['SUBTITLE', 'EOF'],
        ]
        with get_parser('no semicolon.sm') as parser:
            for i, param in enumerate(parser):
                self.assertEqual(param, expected[i])
            self.assertEqual(i + 1, len(expected))

    def test_unicode(self):
        expected = [
            ['TITLE', '実例'],
            ['ARTIST', '楽士'],
        ]
        with get_parser('unicode.sm') as parser:
            for i, param in enumerate(parser):
                self.assertEqual(param, expected[i])
            self.assertEqual(i + 1, len(expected))


class TestChart(unittest.TestCase):

    def test_init_msd(self):
        chart = get_default_chart()
        self.assertEqual(chart.stepstype, 'dance-single')
        self.assertEqual(chart.description, 'Ash Garcia')
        self.assertEqual(chart.difficulty, 'Challenge')
        self.assertEqual(chart.meter, 12)
        self.assertEqual(chart.radar, 'radar')
        self.assertEqual(chart.notes, '0000')

    def test_init_chart(self):
        chart1 = get_default_chart()
        chart2 = SMChart(chart1)
        self.assertEqual(chart1, chart2)
        self.assertIsNot(chart1, chart2)
        self.assertEqual(chart1.notes, chart2.notes)
        self.assertIsNot(chart1.notes, chart2.notes)
        chart1.meter = 100
        self.assertNotEqual(chart1.meter, chart2.meter)

    def test_repr(self):
        chart = get_default_chart()
        self.assertEqual(repr(chart),
                         '<SMChart: dance-single Challenge 12 (Ash Garcia)>')
        chart.description = ''
        self.assertEqual(repr(chart), '<SMChart: dance-single Challenge 12>')


class TestCharts(unittest.TestCase):

    def test_get(self):
        charts = get_simfile('Tribal Style.sm').charts
        chart_sx = charts.get(stepstype='dance-single', difficulty='Challenge')
        self.assertIsInstance(chart_sx, SMChart)
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
            SMCharts([chart_sx])
        )
        self.assertEqual(
            charts.filter(difficulty='Challenge'),
            SMCharts([chart_sx, chart_dx])
        )
        self.assertEqual(len(charts.filter(stepstype='dance-single')), 5)
        self.assertEqual(len(charts.filter(stepstype='dance-double')), 4)
        # A filter that matches nothing should return an empty Charts object,
        # as opposed to raising an error
        self.assertFalse(charts.filter(stepstype='dance-triple'))

    def test_repr(self):
        charts = get_simfile('Tribal Style.sm').charts
        repr_charts = repr(charts)
        self.assertTrue(repr_charts.startswith('SMCharts([<SMChart:'))
        self.assertTrue(repr_charts.endswith('>])'))


class TestTiming(unittest.TestCase):

    def test_bpms(self):
        bpms = get_simfile('Robotix.sm').bpms
        self.assertIsInstance(bpms, Timing)
        self.assertEqual(bpms[0][0], 0)
        self.assertEqual(bpms[0][1], 150)
        self.assertEqual(bpms[1][0], 144)
        self.assertEqual(bpms[1][1], decimal.Decimal('170.001'))

    def test_stops(self):
        stops = get_simfile('Robotix.sm').stops
        self.assertIsInstance(stops, Timing)
        self.assertEqual(stops[0][0], 313)
        self.assertEqual(stops[0][1], decimal.Decimal('0.400'))
        self.assertEqual(stops[1][0], 344)
        self.assertEqual(stops[1][1], decimal.Decimal('0.400'))


class TestSimfile(unittest.TestCase):

    def test_init_file(self):
        with open('testdata/Tribal Style.sm', 'r', encoding='utf-8') as infile:
            sm = SMSimfile(infile)
        # Check that basic properties were parsed
        self.assertEqual(sm.title, 'Tribal Style')
        self.assertEqual(sm.artist, 'KaW')
        # File object input should store the filename
        self.assertEqual(sm.filename, 'testdata/Tribal Style.sm')

    def test_from_string(self):
        with open('testdata/Tribal Style.sm', 'r', encoding='utf-8') as infile:
            sm1 = SMSimfile(infile)
        # String input should be identical to filename input
        with codecs.open('testdata/Tribal Style.sm', 'r', 'utf-8') as sm_file:
            sm2 = SMSimfile.from_string(sm_file.read())
        self.assertEqual(sm1, sm2)
        # String input should have no filename
        self.assertFalse(sm2.filename)
        # No arguments is equivalent to an empty string argument
        blank = SMSimfile()
        self.assertEqual(blank, SMSimfile.from_string(''))

    def test_eq(self):
        # Equality is indirectly tested in other methods, but it has subtleties
        # that need to be specifically tested that don't fit in elsewhere.
        sm = SMSimfile.from_string('#TITLE:A;#SUBTITLE:B;')
        sm_outside_ws = SMSimfile.from_string(' #TITLE:A;\r\n\t#SUBTITLE:B; \r\n\r\n')
        sm_inside_ws = SMSimfile.from_string('#TITLE:\tA\n;#\r\rSUBTITLE:\nB\t\n;')
        sm_order = SMSimfile.from_string('#SUBTITLE:B;#TITLE:A;')
        sm_identifier_case = SMSimfile.from_string('#Title:A;#subtitle:B;')
        sm_value_case = SMSimfile.from_string('#TITLE:a;#SUBTITLE:b;')
        sm_chart = SMSimfile.from_string('#TITLE:A;#SUBTITLE:B;#NOTES::::1::;')
        sm_chart_2 = SMSimfile.from_string('#TITLE:A;#SUBTITLE:B;#NOTES::::2::;')
        self.assertEqual(sm, sm_outside_ws)
        self.assertNotEqual(sm, sm_inside_ws)
        self.assertNotEqual(sm, sm_order)
        self.assertEqual(sm, sm_identifier_case)
        self.assertNotEqual(sm, sm_value_case)
        self.assertNotEqual(sm, sm_chart)
        self.assertNotEqual(sm_chart, sm_chart_2)

    def test_save(self):
        try:
            sm1 = get_simfile('Tribal Style.sm')
            sm1.save('testdata/save.sm')
            sm2 = get_simfile('save.sm', {})
            self.assertEqual(sm1, sm2)
            sm2.title = 'Overwritten'
            sm2.save()
            sm3 = get_simfile('save.sm', {})
            self.assertEqual(sm2, sm3)
            self.assertNotEqual(sm1, sm3)
            sm4 = SMSimfile.from_string('#TITLE:String;')
            self.assertRaises(ValueError, sm4.save)
        finally:
            os.remove('testdata/save.sm')

    def test_parameter_properties(self):
        sm = get_simfile('Tribal Style.sm')
        self.assertEqual(sm.title, 'Tribal Style')
        self.assertEqual(sm.subtitle, '')
        self.assertEqual(sm.artist, 'KaW')
        self.assertEqual(sm.samplestart, decimal.Decimal('41.060'))
        self.assertEqual(sm.samplelength, decimal.Decimal('13.840'))
        self.assertIsInstance(sm.bpms, Timing)
        self.assertIsInstance(sm.stops, Timing)
        

    def test_repr(self):
        sm = get_simfile('Tribal Style.sm', {})
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style>')
        # Check that parentheses are only added when necessary
        sm.subtitle = 'Subtitle'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style (Subtitle)>')
        sm.subtitle = '(Subtitle)'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style (Subtitle)>')
        sm.subtitle = '[Subtitle]'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style [Subtitle]>')
        sm.subtitle = '{Subtitle}'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style {Subtitle}>')
        # One is not enough
        sm.subtitle = '(Subtitle'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style ((Subtitle)>')
        # No title means no ": " after the class name
        del sm.title
        self.assertEqual(repr(sm), '<SMSimfile>')
        del sm.subtitle
        self.assertEqual(repr(sm), '<SMSimfile>')


if __name__ == '__main__':
    unittest.main()
