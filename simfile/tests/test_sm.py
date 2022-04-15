from copy import deepcopy
import unittest

from ..sm import *


def testing_chart():
    return (
        '\n'
        '     dance-single:\n'
        '     Brackets:\n'
        '     Edit:\n'
        '     12:\n'
        '     0.793,1.205,0.500,0.298,0.961:\n'
        '0000\n'
        '0000\n'
        '0000\n'
        '0000\n'
    )


def testing_charts():
    variants = tuple(SMChart.from_str(testing_chart()) for _ in range(7))
    variants[1].stepstype = 'dance-double'
    variants[2].description = 'Footswitches'
    variants[3].difficulty = 'Challenge'
    variants[4].meter = '13'
    variants[5].radarvalues = '1.000,1.000,1.000,1.000,1.000'
    variants[6].notes = '1000\n0100\n0010\n0001'
    return variants


def testing_simfile():
    sm = SMSimfile.blank()
    sm.title = 'My Cool Song'
    sm.artist = 'My Cool Alias'
    sm.charts.extend(testing_charts())
    return str(sm)


class TestSMChart(unittest.TestCase):
    
    def test_init_and_properties(self):
        unit = SMChart.from_str(testing_chart())

        self.assertEqual('dance-single', unit.stepstype)
        self.assertEqual('Brackets', unit.description)
        self.assertEqual('Edit', unit.difficulty)
        self.assertEqual('12', unit.meter)
        self.assertEqual('0.793,1.205,0.500,0.298,0.961', unit.radarvalues)
        self.assertEqual('0000\n0000\n0000\n0000', unit.notes)
    
    def test_serialize(self):
        unit = SMChart.from_str(testing_chart())

        self.assertEqual(f'#NOTES:{testing_chart()};', str(unit))
    
    def test_serialize_with_escapes(self):
        unit = SMChart.from_str(testing_chart())
        unit.description = 'A;B//C\\D:E'
        expected_substring = 'A\\;B\\//C\\\\D\\:E:\n'

        self.assertIn(expected_substring, str(unit))

    def test_eq(self):
        variants = testing_charts()
        base = variants[0]
        copy = deepcopy(base)

        # Identity check
        self.assertEqual(base, base)

        # Equality check
        self.assertEqual(base, copy)

        # Inequality checks
        self.assertNotEqual(base, variants[1])
        self.assertNotEqual(base, variants[2])
        self.assertNotEqual(base, variants[3])
        self.assertNotEqual(base, variants[4])
        self.assertNotEqual(base, variants[5])
        self.assertNotEqual(base, variants[6])
    
    def test_getitem(self):
        unit = SMChart.from_str(testing_chart())

        self.assertEqual(unit['STEPSTYPE'], unit.stepstype)
        self.assertRaises(KeyError, unit.__getitem__, 'stepstype')

    def test_repr(self):
        unit = SMChart.from_str(testing_chart())

        self.assertEqual('<SMChart: dance-single Edit 12>', repr(unit))
    
    def test_preserves_extra_data(self):
        extra_data = 'extra:data'
        chart_with_extra_data = testing_chart() + ':' + extra_data
        unit = SMChart.from_str(chart_with_extra_data)

        self.assertEqual(['extra', 'data'], unit.extradata)
        self.assertTrue(str(unit).endswith(f':{extra_data};'))


class TestSMCharts(unittest.TestCase):
    
    def test_init_and_list_methods(self):
        unit = SMCharts(testing_charts())
        
        self.assertEqual(7, len(unit))
        for chart in unit:
            self.assertIsInstance(chart, SMChart)
    
    def test_serialize(self):
        unit = SMCharts(testing_charts())

        serialized = str(unit)
        self.assertTrue(serialized.startswith(str(testing_charts()[0])))
        self.assertTrue(serialized.endswith(str(testing_charts()[-1]) + '\n'))
    
    def test_repr(self):
        chart = SMChart.from_str(testing_chart())
        repr_chart = repr(chart)
        unit = SMCharts([chart])

        self.assertEqual(f'SMCharts([{repr_chart}])', repr(unit))

        unit.append(chart)

        self.assertEqual(f'SMCharts([{repr_chart}, {repr_chart}])', repr(unit))


class TestSMSimfile(unittest.TestCase):
    
    def test_init_and_properties(self):
        unit = SMSimfile(string=testing_simfile())
        
        self.assertEqual('My Cool Song', unit['TITLE'])
        self.assertEqual('My Cool Song', unit.title)
        self.assertEqual('My Cool Alias', unit['ARTIST'])
        self.assertEqual('My Cool Alias', unit.artist)
        self.assertNotIn('NONEXISTENT', unit)
        self.assertEqual(7, len(unit.charts))
    
    def test_init_handles_freezes_property(self):
        with_stops = SMSimfile(string=testing_simfile())
        with_freezes_data = testing_simfile().replace(
            '#STOPS:',
            '#FREEZES:',
        )
        with_freezes = SMSimfile(string=with_freezes_data)
        self.assertEqual(with_stops.stops, with_freezes.stops)
        self.assertNotIn('STOPS', with_freezes)
        self.assertIn('FREEZES', with_freezes)
    
    def test_init_handles_animations_property(self):
        with_bgchanges = SMSimfile(string=testing_simfile())
        with_animations_data = testing_simfile().replace(
            '#BGCHANGES:',
            '#ANIMATIONS:',
        )
        with_animations = SMSimfile(string=with_animations_data)
        self.assertEqual(with_bgchanges.bgchanges, with_animations.bgchanges)
        self.assertNotIn('BGCHANGES', with_animations)
        self.assertIn('ANIMATIONS', with_animations)
        

    def test_repr(self):
        unit = SMSimfile(string=testing_simfile())

        self.assertEqual('<SMSimfile: My Cool Song>', repr(unit))

        unit['SUBTITLE'] = '(edited)'

        self.assertEqual('<SMSimfile: My Cool Song (edited)>', repr(unit))

    def test_eq(self):
        variants = tuple(SMSimfile(string=testing_simfile()) for _ in range(3))
        variants[1]['TITLE'] = 'Cool Song 2'
        variants[2].charts[0].description = 'Footswitches'
        base = variants[0]
        copy = deepcopy(base)

        # Identity check
        self.assertEqual(base, base)

        # Equality check
        self.assertEqual(base, copy)

        # Inequality checks
        self.assertNotEqual(base, variants[1])
        self.assertNotEqual(base, variants[2])
    
    def test_charts(self):
        unit = SMSimfile(string=testing_simfile())
        
        self.assertIsInstance(unit.charts, SMCharts)
        self.assertEqual(7, len(unit.charts))
        self.assertIsInstance(unit.charts[0], SMChart)
        
        unit.charts = unit.charts[:3]
        self.assertEqual(3, len(unit.charts))

        unit.charts = SMCharts()
        self.assertEqual(0, len(unit.charts))
