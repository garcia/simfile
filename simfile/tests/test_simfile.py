#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals
import codecs
import decimal
from fractions import Fraction
import os
import unittest

import simfile
from simfile.timing import Timing
from simfile.sm import *


def get_simfile(filename, cache={}):
    if not filename in cache:
        cache[filename] = simfile.open(os.path.join('testdata', filename))
    return cache[filename]


def get_default_chart():
    return SMChart(
        'dance-single:'
        'Brackets:'
        'Edit:'
        '12:'
        '0.793,1.205,0.500,0.298,0.961:'
        '0000\n0000\n0000\n0000'
    )


class TestChart(unittest.TestCase):

    def test_init(self):
        chart = get_default_chart()
        self.assertEqual(chart.stepstype, 'dance-single')
        self.assertEqual(chart.description, 'Brackets')
        self.assertEqual(chart.difficulty, 'Edit')
        self.assertEqual(chart.meter, 12)
        self.assertEqual(chart.radarvalues, '0.793,1.205,0.500,0.298,0.961')
        self.assertEqual(chart.notes, '0000\n0000\n0000\n0000')

    def test_repr(self):
        chart = get_default_chart()
        self.assertEqual(repr(chart),
                         '<SMChart: dance-single Edit 12>')


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
        
        filter_result = charts.filter(stepstype='dance-single', difficulty='Challenge')
        filter_iter = iter(filter_result)
        self.assertEqual(chart_sx, next(filter_iter))
        self.assertRaises(StopIteration, next, filter_iter)

        filter_result = charts.filter(difficulty='Challenge')
        filter_iter = iter(filter_result)
        self.assertEqual(chart_sx, next(filter_iter))
        self.assertEqual(chart_dx, next(filter_iter))
        self.assertRaises(StopIteration, next, filter_iter)

        self.assertEqual(len(list(charts.filter(stepstype='dance-single'))), 5)
        self.assertEqual(len(list(charts.filter(stepstype='dance-double'))), 4)
        # A filter that matches nothing should yield nothing, not raise
        self.assertFalse(list(charts.filter(stepstype='dance-triple')))

    def test_repr(self):
        charts = get_simfile('Tribal Style.sm').charts
        repr_charts = repr(charts)
        self.assertTrue(repr_charts.startswith('SMCharts([<SMChart:'))
        self.assertTrue(repr_charts.endswith('>])'))


class TestTiming(unittest.TestCase):

    def test_bpms(self):
        bpms = Timing(get_simfile('Robotix.sm')['BPMS'])
        self.assertIsInstance(bpms, Timing)
        self.assertEqual(bpms[0][0], 0)
        self.assertEqual(bpms[0][1], 150)
        self.assertEqual(bpms[1][0], 144)
        self.assertEqual(bpms[1][1], decimal.Decimal('170.001'))

    def test_stops(self):
        stops = Timing(get_simfile('Robotix.sm')['STOPS'])
        self.assertIsInstance(stops, Timing)
        self.assertEqual(stops[0][0], 313)
        self.assertEqual(stops[0][1], decimal.Decimal('0.400'))
        self.assertEqual(stops[1][0], 344)
        self.assertEqual(stops[1][1], decimal.Decimal('0.400'))


class TestSimfile(unittest.TestCase):

    def test_init_file(self):
        with open('testdata/Tribal Style.sm', 'r', encoding='utf-8') as infile:
            sm = SMSimfile(file=infile)
        # Check that basic properties were parsed
        self.assertEqual(sm['TITLE'], 'Tribal Style')
        self.assertEqual(sm['ARTIST'], 'KaW')

    def test_from_string(self):
        with open('testdata/Tribal Style.sm', 'r', encoding='utf-8') as infile:
            sm1 = SMSimfile(file=infile)
        # String input should be identical to filename input
        with codecs.open('testdata/Tribal Style.sm', 'r', 'utf-8') as sm_file:
            sm2 = simfile.loads(sm_file.read())
        self.assertEqual(sm1, sm2)
        # Empty string argument is valid
        blank = SMSimfile(string='')
        self.assertEqual(blank, simfile.loads(''))

    def test_eq(self):
        # Equality is indirectly tested in other methods, but it has subtleties
        # that need to be specifically tested that don't fit in elsewhere.
        sm = simfile.loads('#TITLE:A;#SUBTITLE:B;')
        sm_outside_ws = simfile.loads(' #TITLE:A;\r\n\t#SUBTITLE:B; \r\n\r\n')
        sm_inside_ws = simfile.loads('#TITLE:\tA\n;#\r\rSUBTITLE:\nB\t\n;')
        sm_order = simfile.loads('#SUBTITLE:B;#TITLE:A;')
        sm_identifier_case = simfile.loads('#Title:A;#subtitle:B;')
        sm_value_case = simfile.loads('#TITLE:a;#SUBTITLE:b;')
        sm_chart = simfile.loads('#TITLE:A;#SUBTITLE:B;#NOTES::::1::;')
        sm_chart_2 = simfile.loads('#TITLE:A;#SUBTITLE:B;#NOTES::::2::;')
        self.assertEqual(sm, sm_outside_ws)
        self.assertNotEqual(sm, sm_inside_ws)
        self.assertNotEqual(sm, sm_order)
        self.assertEqual(sm, sm_identifier_case)
        self.assertNotEqual(sm, sm_value_case)
        self.assertNotEqual(sm, sm_chart)
        self.assertNotEqual(sm_chart, sm_chart_2)

    def test_parameter_properties(self):
        sm = get_simfile('Tribal Style.sm')
        self.assertEqual(sm['TITLE'], 'Tribal Style')
        self.assertEqual(sm['SUBTITLE'], '')
        self.assertEqual(sm['ARTIST'], 'KaW')
        self.assertEqual(sm['SAMPLESTART'], '41.060')
        self.assertEqual(sm['SAMPLELENGTH'], '13.840')
        self.assertIsInstance(Timing(sm['BPMS']), Timing)
        self.assertIsInstance(Timing(sm['STOPS']), Timing)

    def test_repr(self):
        sm = get_simfile('Tribal Style.sm', {})
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style>')
        sm['SUBTITLE'] = 'Subtitle'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style Subtitle>')
        sm['SUBTITLE'] = '(Subtitle)'
        self.assertEqual(repr(sm), '<SMSimfile: Tribal Style (Subtitle)>')
        del sm['SUBTITLE']
        del sm['TITLE']
        self.assertEqual(repr(sm), '<SMSimfile>')


if __name__ == '__main__':
    unittest.main()
