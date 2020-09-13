import unittest

from ..sm import *


class TestSMChart(unittest.TestCase):
    
    def test_constructor(self):
        unit = SMChart("\n"
            "     dance-single:\n"
            "     Brackets:\n"
            "     Edit:\n"
            "     12:\n"
            "     0.793,1.205,0.500,0.298,0.961:\n"
            "  \n"
            "0000\n"
            "0000\n"
            "0000\n"
            "0000\n")

        self.assertEqual("dance-single", unit.stepstype)
        self.assertEqual("Brackets", unit.description)
        self.assertEqual("Edit", unit.difficulty)
        self.assertEqual(12, unit.meter)
        self.assertEqual('0.793,1.205,0.500,0.298,0.961', unit.radarvalues)
        self.assertEqual('0000\n0000\n0000\n0000', unit.notes)


if __name__ == "__main__":
    unittest.main()