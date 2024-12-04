import unittest
from .helpers.fake_simfile import FakeSimfile

class TestSimfileObjects(unittest.TestCase):
    def test_newline_detection(self):
        for sim in FakeSimfile.make_blank():
            SimfileType = type(sim)
            with self.subTest(SimfileType):
                sim_with_windows_newlines = SimfileType(string=str(sim).replace('\n', '\r\n'))
                sim_with_windows_newlines['CUSTOMFIELD'] = 'customvalue'
                self.assertEqual(sim_with_windows_newlines._default_parameter.suffix, ';\r\n')
                self.assertIn('#CUSTOMFIELD:customvalue;\r\n', str(sim_with_windows_newlines))