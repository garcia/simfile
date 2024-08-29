import unittest

import simfile
from simfile.sm import SMChart, SMSimfile
from simfile.ssc import SSCChart, SSCSimfile
from tests.helpers.fake_simfile import FakeChart, FakeSimfile


class TestFakeChart(unittest.TestCase):
    def test_fake_blank(self):
        encountered_sm = False
        encountered_ssc = False

        for fake in FakeChart.make_blank():
            if isinstance(fake, SMChart):
                encountered_sm = True
            if isinstance(fake, SSCChart):
                encountered_ssc = True
            self.assertEqual(type(fake).blank(), fake)

        self.assertTrue(encountered_sm)
        self.assertTrue(encountered_ssc)

    def test_fake_with_fields(self):
        encountered_sm = False
        encountered_ssc = False

        for fake in FakeChart().with_fields(
            stepstype="dance-double",
            description="My cool chart",
            difficulty="Challenge",
            meter="10",
        ):
            if isinstance(fake, SMChart):
                encountered_sm = True
            if isinstance(fake, SSCChart):
                encountered_ssc = True
            self.assertEqual("dance-double", fake.stepstype)
            self.assertEqual("My cool chart", fake.description)
            self.assertEqual("Challenge", fake.difficulty)
            self.assertEqual("10", fake.meter)

        self.assertTrue(encountered_sm)
        self.assertTrue(encountered_ssc)

    def test_fake_with_fields_and_combinations(self):
        encountered_new_field = False
        encountered_orig_field = False

        for fake in FakeChart().with_fields(
            combinations=True,
            stepstype="dance-double",
            description="My cool chart",
            difficulty="Challenge",
            meter="10",
        ):
            if fake.stepstype == "dance-double":
                encountered_new_field = True
                self.assertEqual("My cool chart", fake.description)
                self.assertEqual("Challenge", fake.difficulty)
                self.assertEqual("10", fake.meter)
            else:
                encountered_orig_field = True
                self.assertNotEqual("(My cool subtitle)", fake.description)
                self.assertNotEqual("My cool artist", fake.difficulty)
                self.assertNotEqual("0.000=180.000", fake.meter)

        self.assertTrue(encountered_new_field)
        self.assertTrue(encountered_orig_field)

    def test_of_type(self):
        for fake in FakeChart().of_type(SMChart):
            self.assertIsInstance(fake, SMChart)
        for fake in FakeChart().of_type(SSCChart):
            self.assertIsInstance(fake, SSCChart)


class TestFakeSimfile(unittest.TestCase):
    def test_fake_blank(self):
        encountered_sm = False
        encountered_ssc = False

        for fake in FakeSimfile.make_blank():
            if isinstance(fake, SMSimfile):
                encountered_sm = True
            if isinstance(fake, SSCSimfile):
                encountered_ssc = True
            self.assertEqual(type(fake).blank(), fake)

        self.assertTrue(encountered_sm)
        self.assertTrue(encountered_ssc)

    def test_fake_with_fields(self):
        encountered_sm = False
        encountered_ssc = False

        for fake in FakeSimfile().with_fields(
            title="My cool song",
            subtitle="(My cool subtitle)",
            artist="My cool artist",
            bpms="0.000=180.000",
        ):
            if isinstance(fake, SMSimfile):
                encountered_sm = True
            if isinstance(fake, SSCSimfile):
                encountered_ssc = True
            self.assertEqual("My cool song", fake.title)
            self.assertEqual("(My cool subtitle)", fake.subtitle)
            self.assertEqual("My cool artist", fake.artist)
            self.assertEqual("0.000=180.000", fake.bpms)

        self.assertTrue(encountered_sm)
        self.assertTrue(encountered_ssc)

    def test_fake_with_fields_and_combinations(self):
        encountered_new_field = False
        encountered_orig_field = False

        for fake in FakeSimfile().with_fields(
            combinations=True,
            title="My cool song",
            subtitle="(My cool subtitle)",
            artist="My cool artist",
            bpms="0.000=180.000",
        ):
            if fake.title == "My cool song":
                encountered_new_field = True
                self.assertEqual("(My cool subtitle)", fake.subtitle)
                self.assertEqual("My cool artist", fake.artist)
                self.assertEqual("0.000=180.000", fake.bpms)
            else:
                encountered_orig_field = True
                self.assertNotEqual("(My cool subtitle)", fake.subtitle)
                self.assertNotEqual("My cool artist", fake.artist)
                self.assertNotEqual("0.000=180.000", fake.bpms)

        self.assertTrue(encountered_new_field)
        self.assertTrue(encountered_orig_field)

    def test_of_type(self):
        for fake in FakeSimfile().of_type(SMSimfile):
            self.assertIsInstance(fake, SMSimfile)
        for fake in FakeSimfile().of_type(SSCSimfile):
            self.assertIsInstance(fake, SSCSimfile)
