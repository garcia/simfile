from copy import deepcopy
import unittest

from ..sm import *


def testing_chart():
    return (
        "\n"
        "     dance-single:\n"
        "     Brackets:\n"
        "     Edit:\n"
        "     12:\n"
        "     0.793,1.205,0.500,0.298,0.961:\n"
        "0000\n"
        "0000\n"
        "0000\n"
        "0000\n"
    )


def testing_charts():
    variants = tuple(SMChart(testing_chart()) for _ in range(7))
    variants[1].stepstype = 'dance-double'
    variants[2].description = 'Footswitches'
    variants[3].difficulty = 'Challenge'
    variants[4].meter = 13
    variants[5].radarvalues = '1.000,1.000,1.000,1.000,1.000'
    variants[6].notes = '1000\n0100\n0010\n0001'
    return variants


def testing_simfile():
    return (
        "#TITLE:My Cool Song;\n"
        "#ARTIST:My Cool Alias;\n"
    )
    SMCharts(testing_charts()).serialize()


class TestSMChart(unittest.TestCase):
    
    def test_init_and_properties(self):
        unit = SMChart(testing_chart())

        self.assertEqual('dance-single', unit.stepstype)
        self.assertEqual('Brackets', unit.description)
        self.assertEqual('Edit', unit.difficulty)
        self.assertEqual(12, unit.meter)
        self.assertEqual('0.793,1.205,0.500,0.298,0.961', unit.radarvalues)
        self.assertEqual('0000\n0000\n0000\n0000', unit.notes)
    
    def test_serialize(self):
        unit = SMChart(testing_chart())

        self.assertEqual(f'#NOTES:{testing_chart()};', unit.serialize())

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

    def test_repr(self):
        unit = SMChart(testing_chart())

        self.assertEqual('<SMChart: dance-single Edit 12>', repr(unit))


class TestSMCharts(unittest.TestCase):
    
    def test_init_and_list_methods(self):
        unit = SMCharts(testing_charts())
        
        self.assertEqual(7, len(unit))
        for chart in unit:
            self.assertIsInstance(chart, SMChart)
    
    def test_serialize(self):
        unit = SMCharts(testing_charts())

        value = unit.serialize()
    
    def test_repr(self):
        chart = SMChart(testing_chart())
        repr_chart = repr(chart)
        unit = SMCharts([chart])

        self.assertEqual(f'SMCharts([{repr_chart}])', repr(unit))

        unit.append(chart)

        self.assertEqual(f'SMCharts([{repr_chart}, {repr_chart}])', repr(unit))


class TestSMSimfile(unittest.TestCase):
    def test_init(self):
        unit = SMSimfile(testing_simfile())




if __name__ == "__main__":
    unittest.main()