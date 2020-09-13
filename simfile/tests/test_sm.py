from copy import deepcopy
import unittest

from ..sm import *


class TestSMChart(unittest.TestCase):

    TEST_CHART = (
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
    
    def test_constructor_and_properties(self):
        unit = SMChart(TestSMChart.TEST_CHART)

        self.assertEqual('dance-single', unit.stepstype)
        self.assertEqual('Brackets', unit.description)
        self.assertEqual('Edit', unit.difficulty)
        self.assertEqual(12, unit.meter)
        self.assertEqual('0.793,1.205,0.500,0.298,0.961', unit.radarvalues)
        self.assertEqual('0000\n0000\n0000\n0000', unit.notes)
    
    def test_serialize(self):
        unit = SMChart(TestSMChart.TEST_CHART)

        self.assertEqual(f'#NOTES:{TestSMChart.TEST_CHART};', unit.serialize())

    def test_eq(self):
        unit = SMChart(TestSMChart.TEST_CHART)
        variants = tuple(deepcopy(unit) for _ in range(7))
        variants[1].stepstype = 'dance-double'
        variants[2].description = 'Footswitches'
        variants[3].difficulty = 'Challenge'
        variants[4].meter = 13
        variants[5].radarvalues = '1.000,1.000,1.000,1.000,1.000'
        variants[6].notes = '1000\n0100\n0010\n0001'

        # Identity check
        self.assertEqual(unit, unit)

        # Equality check
        self.assertEqual(unit, variants[0])

        # Inequality checks
        self.assertNotEqual(unit, variants[1])
        self.assertNotEqual(unit, variants[2])
        self.assertNotEqual(unit, variants[3])
        self.assertNotEqual(unit, variants[4])
        self.assertNotEqual(unit, variants[5])
        self.assertNotEqual(unit, variants[6])

    def test_repr(self):
        unit = SMChart(TestSMChart.TEST_CHART)
        
        self.assertEqual('<SMChart: dance-single Edit 12>', repr(unit))


if __name__ == "__main__":
    unittest.main()