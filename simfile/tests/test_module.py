from pyfakefs.fake_filesystem_unittest import TestCase

import simfile
from simfile.sm import SMSimfile
from simfile.ssc import SSCSimfile
from simfile.tests import test_sm, test_ssc

class TestSimfileModule(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        with open('testing_simfile.sm', 'w') as writer:
            writer.write(test_sm.testing_simfile())
        with open('testing_simfile.ssc', 'w') as writer:
            writer.write(test_ssc.testing_simfile())

    def test_load_with_sm_extension(self):
        with open('testing_simfile.sm', 'r') as reader:
            sm = simfile.load(reader)
        
        self.assertIsInstance(sm, SMSimfile)
        self.assertEqual(SMSimfile(string=test_sm.testing_simfile()), sm)

    def test_load_with_ssc_extension(self):
        with open('testing_simfile.ssc', 'r') as reader:
            ssc = simfile.load(reader)
        
        self.assertIsInstance(ssc, SSCSimfile)
        self.assertEqual(SSCSimfile(string=test_ssc.testing_simfile()), ssc)

    def test_loads_with_sm_contents(self):
        sm = simfile.loads(test_sm.testing_simfile())

        self.assertIsInstance(sm, SMSimfile)
        self.assertEqual(SMSimfile(string=test_sm.testing_simfile()), sm)

    def test_loads_with_ssc_contents(self):
        ssc = simfile.loads(test_ssc.testing_simfile())

        self.assertIsInstance(ssc, SSCSimfile)
        self.assertEqual(SSCSimfile(string=test_ssc.testing_simfile()), ssc)

    def test_open_with_sm_file(self):
        sm = simfile.open('testing_simfile.sm')
        
        self.assertIsInstance(sm, SMSimfile)
        self.assertEqual(SMSimfile(string=test_sm.testing_simfile()), sm)

    def test_open_with_ssc_file(self):
        ssc = simfile.open('testing_simfile.ssc')
        
        self.assertIsInstance(ssc, SSCSimfile)
        self.assertEqual(SSCSimfile(string=test_ssc.testing_simfile()), ssc)

    def test_mutate_with_sm_file(self):
        with simfile.mutate('testing_simfile.sm') as sm:
            sm['TITLE'] = 'Cool Song 2'

        sm = simfile.open('testing_simfile.sm')

        self.assertEqual('Cool Song 2', sm['TITLE'])

    def test_mutate_with_ssc_file(self):
        with simfile.mutate('testing_simfile.ssc') as ssc:
            ssc['TITLE'] = 'Cool Song 2'

        ssc = simfile.open('testing_simfile.ssc')

        self.assertEqual('Cool Song 2', ssc['TITLE'])