#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals
import codecs
import decimal
from fractions import Fraction
import os
import unittest

from simfile import *
from simfile.msd import MSDParser

def get_parser(filename):
    return MSDParser(codecs.open(os.path.join('testdata', filename), 'r',
        encoding='utf-8'))

def get_simfile(filename, cache={}):
    if not filename in cache:
        cache[filename] = Simfile(os.path.join('testdata', filename))
    return cache[filename]

def get_default_chart():
    return Chart([
        'dance-single', 'Grant Garcia', 'Challenge', '12', '?', '0000'
    ])


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
            ['ARTIST', 'Grant/Garcia'],
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
            ['TITLE', 'No semicolon'],
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


class TestNotes(unittest.TestCase):
    
    def test_init_str(self):
        notes = Notes('0000')
        # bool(notes) should be False because it contains no arrows
        self.assertFalse(notes)
        self.assertEqual(notes.arrows, 4)
        # Different arrow count between rows
        self.assertRaises(ValueError, Notes, '0000\n000')
        # Check if notes are populated in the correct positions
        notes = Notes('1000\n0100\n0010\n0001,')
        self.assertEqual(notes[0], [Fraction(0), '1000'])
        self.assertEqual(notes[1], [Fraction(1), '0100'])
        self.assertEqual(notes[2], [Fraction(2), '0010'])
        self.assertEqual(notes[3], [Fraction(3), '0001'])
        self.assertEqual(len(notes), 4)
        # Fractional values
        notes = Notes('1000\n0100\n0010\n0001,'
                      '1110\n1101\n1011\n0111\n1011\n1101\n1110\n1111,')
        self.assertEqual(notes[3], [Fraction(3), '0001'])
        self.assertEqual(notes[4], [Fraction(8, 2), '1110'])
        self.assertEqual(notes[5], [Fraction(9, 2), '1101'])
        self.assertEqual(notes[6], [Fraction(10, 2), '1011'])
        self.assertEqual(notes[7], [Fraction(11, 2), '0111'])
        self.assertEqual(notes[8], [Fraction(12, 2), '1011'])
        self.assertEqual(notes[9], [Fraction(13, 2), '1101'])
        self.assertEqual(notes[10], [Fraction(14, 2), '1110'])
        self.assertEqual(notes[11], [Fraction(15, 2), '1111'])
    
    def test_init_notes(self):
        notes1 = Notes('1010\n0101\n1001\n0110,')
        notes2 = Notes(notes1)
        self.assertEqual(notes1, notes2)
        self.assertIsNot(notes1, notes2)
        self.assertIsNot(notes1[0], notes2[0])
        notes1[0][0] = Fraction(1, 2)
        self.assertNotEqual(notes1[0][0], notes2[0][0])
        notes1[0][1] = '1111'
        self.assertNotEqual(notes1[0][1], notes2[0][1])
    
    def test_repr(self):
        self.assertTrue(repr(Notes('0000')).startswith(
            '<simfile.simfile.Notes object at 0x'
        ))
    
    def test_str(self):
        notes = Notes('1001')
        self.assertEqual(str(notes), unicode(notes).encode('utf-8'))
    
    def test_unicode(self):
        # Get un-parsed notedata
        with get_parser('Tribal Style.sm') as parser:
            for param in parser:
                if param[0] == 'NOTES':
                    notedata = param[-1]
                    break
        notes = Notes(notedata)
        self.assertEqual(unicode(notes), notedata)
    
    def test_insertion(self):
        notes = Notes('1000\n0100\n0000\n0001,')
        self.assertEqual(len(notes), 3)
        # Appending into the middle of the note data
        notes.append([Fraction(2), '0010'])
        self.assertEqual(len(notes), 4)
        self.assertEqual(unicode(notes), '1000\n0100\n0010\n0001')
        # Extending the list at various places in the note data
        notes.extend([[Fraction(3, 2), '1001'], [Fraction(7), '0110']])
        self.assertEqual(unicode(notes),
            '1000\n0000\n0100\n1001\n0010\n0000\n0001\n0000\n,\n'
            '0000\n0000\n0000\n0110'
        )


class TestChart(unittest.TestCase):
    
    def test_init_seq(self):
        chart = Chart([
            'dance-single', 'Grant Garcia', 'Challenge', '12', '?', '0000'
        ])
        self.assertEqual(chart.stepstype, 'dance-single')
        self.assertEqual(chart.description, 'Grant Garcia')
        self.assertEqual(chart.difficulty, 'Challenge')
        # meter should now be an int
        self.assertEqual(chart.meter, 12)
        self.assertEqual(chart.radar, '?')
        self.assertIsInstance(chart.notes, Notes)
    
    def test_init_map(self):
        chart = Chart({
            'stepstype': 'dance-single',
            'description': 'Grant Garcia',
            'difficulty': 'Challenge',
            'meter': '12',
            'radar': '?',
            'notes': '0000',
        })
        self.assertEqual(chart.stepstype, 'dance-single')
        self.assertEqual(chart.description, 'Grant Garcia')
        self.assertEqual(chart.difficulty, 'Challenge')
        self.assertEqual(chart.meter, 12)
        self.assertEqual(chart.radar, '?')
        self.assertIsInstance(chart.notes, Notes)
    
    def test_init_chart(self):
        chart1 = get_default_chart()
        chart2 = Chart(chart1)
        self.assertEqual(chart1, chart2)
        self.assertIsNot(chart1, chart2)
        self.assertEqual(chart1.notes, chart2.notes)
        self.assertIsNot(chart1.notes, chart2.notes)
        chart1.meter = 100
        self.assertNotEqual(chart1.meter, chart2.meter)
    
    def test_repr(self):
        chart = get_default_chart()
        self.assertEqual(repr(chart), '<Chart: dance-single Challenge 12 (Grant Garcia)>')
        chart.description = ''
        self.assertEqual(repr(chart), '<Chart: dance-single Challenge 12>')
    
    def test_str(self):
        chart = get_default_chart()
        self.assertEqual(str(chart), unicode(chart).encode('utf-8'))
    
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
    
    def test_repr(self):
        charts = get_simfile('Tribal Style.sm').charts
        repr_charts = repr(charts)
        self.assertTrue(repr_charts.startswith('Charts([<Chart:'))
        self.assertTrue(repr_charts.endswith('>])'))
    
    def test_str(self):
        charts = get_simfile('Tribal Style.sm').charts
        self.assertEqual(str(charts), unicode(charts).encode('utf-8'))
    
    def test_unicode(self):
        charts = get_simfile('Tribal Style.sm').charts
        unicode_charts = unicode(charts)
        self.assertTrue(unicode_charts.startswith('#NOTES:\n'))
        self.assertEqual(unicode_charts.count('#NOTES:'), 9)
        self.assertTrue(unicode_charts.endswith(';'))


class TestTiming(unittest.TestCase):
    
    def test_bpms(self):
        bpms = get_simfile('Robotix.sm')['BPMS']
        self.assertIsInstance(bpms, Timing)
        self.assertEqual(bpms[0][0], 0)
        self.assertEqual(bpms[0][1], 150)
        self.assertEqual(bpms[1][0], 144)
        self.assertEqual(bpms[1][1], decimal.Decimal('170.001'))
    
    def test_stops(self):
        stops = get_simfile('Robotix.sm')['STOPS']
        self.assertIsInstance(stops, Timing)
        self.assertEqual(stops[0][0], 313)
        self.assertEqual(stops[0][1], decimal.Decimal('0.400'))
        self.assertEqual(stops[1][0], 344)
        self.assertEqual(stops[1][1], decimal.Decimal('0.400'))
    
    def test_str(self):
        stops = get_simfile('Robotix.sm')['STOPS']
        self.assertEqual(str(stops), unicode(stops).encode('utf-8'))
    
    def test_unicode(self):
        stops = get_simfile('Robotix.sm')['STOPS']
        self.assertEqual(unicode(stops), '313.000=0.400,\n344.000=0.400')


class TestSimfile(unittest.TestCase):
    
    def test_init_filename(self):
        sm = Simfile('testdata/Tribal Style.sm')
        self.assertEqual(sm.filename, 'testdata/Tribal Style.sm')
    
    def test_init_file(self):
        sm1 = Simfile('testdata/Tribal Style.sm')
        # File object input should be identical to filename input
        with codecs.open('testdata/Tribal Style.sm', 'r', 'utf-8') as sm_file:
            sm2 = Simfile(sm_file)
        self.assertEqual(sm1, sm2)
        # File object input should retrieve filename
        self.assertEqual(sm1.filename, sm2.filename)
    
    def test_from_string(self):
        sm1 = Simfile('testdata/Tribal Style.sm')
        # String input should be identical to filename input
        with codecs.open('testdata/Tribal Style.sm', 'r', 'utf-8') as sm_file:
            sm2 = Simfile.from_string(sm_file.read())
        self.assertEqual(sm1, sm2)
        # String input should have no filename
        self.assertFalse(sm2.filename)
        # No arguments is equivalent to an empty string argument
        self.assertEqual(Simfile(), Simfile.from_string(''))
    
    def test_eq(self):
        # Equality is indirectly tested in other methods, but it has subtleties
        # that need to be specifically tested that don't fit in elsewhere.
        sm = Simfile.from_string('#TITLE:A;#SUBTITLE:B;')
        sm_whitespace = Simfile.from_string(' #  TITLE   :\tA\n;#\r\rSUBTITLE:\nB\t\n;')
        sm_order = Simfile.from_string('#SUBTITLE:B;#TITLE:A;')
        sm_identifier_case = Simfile.from_string('#Title:A;#subtitle:B;')
        sm_value_case = Simfile.from_string('#TITLE:a;#SUBTITLE:b;')
        sm_chart = Simfile.from_string('#TITLE:A;#SUBTITLE:B;#NOTES::::1::;')
        sm_chart_2 = Simfile.from_string('#TITLE:A;#SUBTITLE:B;#NOTES::::2::;')
        self.assertEqual(sm, sm_whitespace)
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
            sm2['TITLE'] = 'Overwritten'
            sm2.save()
            sm3 = get_simfile('save.sm', {})
            self.assertEqual(sm2, sm3)
            self.assertNotEqual(sm1, sm3)
            sm4 = Simfile.from_string('#TITLE:String;')
            self.assertRaises(ValueError, sm4.save)
        finally:
            os.remove('testdata/save.sm')
    
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
    
    def test_len(self):
        sm_empty = Simfile.from_string('')
        sm_only_params = Simfile.from_string('#TITLE:Title;')
        sm_only_charts = Simfile.from_string(unicode(get_default_chart()))
        sm_both = Simfile.from_string(unicode(sm_only_params) + unicode(sm_only_charts))
        self.assertEqual(len(sm_empty), 0)
        self.assertEqual(len(sm_only_params), 1)
        self.assertEqual(len(sm_only_charts), 1)
        self.assertEqual(len(sm_both), 2)
    
    def test_repr(self):
        sm = get_simfile('Tribal Style.sm', {}) # no cache
        self.assertEqual(repr(sm), '<Simfile: Tribal Style>')
        # Check that parentheses are only added when necessary
        sm['SUBTITLE'] = 'Subtitle'
        self.assertEqual(repr(sm), '<Simfile: Tribal Style (Subtitle)>')
        sm['SUBTITLE'] = '(Subtitle)'
        self.assertEqual(repr(sm), '<Simfile: Tribal Style (Subtitle)>')
        sm['SUBTITLE'] = '[Subtitle]'
        self.assertEqual(repr(sm), '<Simfile: Tribal Style [Subtitle]>')
        sm['SUBTITLE'] = '{Subtitle}'
        self.assertEqual(repr(sm), '<Simfile: Tribal Style {Subtitle}>')
        # One is not enough
        sm['SUBTITLE'] = '(Subtitle'
        self.assertEqual(repr(sm), '<Simfile: Tribal Style ((Subtitle)>')
        # No title means no ": " after the class name
        del sm['TITLE']
        self.assertEqual(repr(sm), '<Simfile>')
        del sm['SUBTITLE']
        self.assertEqual(repr(sm), '<Simfile>')
    
    def test_str(self):
        sm = get_simfile('Tribal Style.sm')
        self.assertEqual(str(sm), unicode(sm).encode('utf-8'))
    
    def test_unicode(self):
        # Comprehensive test that ensures unicode(simfile) returns a perfect
        # representation of the original simfile. This also serves as a "test"
        # of Simfile.save(), which essentially writes unicode(self) to a file.
        sm1 = get_simfile('Tribal Style.sm')
        sm2 = Simfile.from_string(unicode(sm1))
        self.assertEqual(sm1, sm2)


if __name__ == '__main__':
    unittest.main()
