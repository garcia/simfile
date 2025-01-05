import unittest

import simfile
from simfile._private.dedent import dedent_and_trim
from simfile.dir import SimfileDirectory
from simfile.sm import SMChart, SMSimfile
from simfile.ssc import SSCChart
from .helpers.fake_simfile import FakeChart, FakeSimfile


class TestSimfileObjects(unittest.TestCase):
    def test_newline_detection(self):
        for sim in FakeSimfile.make_blank():
            SimfileType = type(sim)
            with self.subTest(SimfileType):
                sim_with_windows_newlines = SimfileType(
                    string=str(sim).replace("\n", "\r\n")
                )
                sim_with_windows_newlines["CUSTOMFIELD"] = "customvalue"
                self.assertEqual(
                    sim_with_windows_newlines._default_parameter.suffix, ";\r\n"
                )
                self.assertIn(
                    "#CUSTOMFIELD:customvalue;\r\n", str(sim_with_windows_newlines)
                )

    def test_chart_exactness(self):
        for chart in FakeChart.make_blank():
            ChartType = type(chart)
            with self.subTest(ChartType):
                stringified = str(chart)
                if ChartType is SMChart:
                    double_stringified = str(SMSimfile(string=str(chart)).charts[0])
                else:
                    double_stringified = str(SSCChart.from_str(str(chart)))
                self.assertEqual(stringified, double_stringified)

    # New properties should go above chart comments, not below them
    def test_whitespace_reorganization(self):
        sd = SimfileDirectory("testdata/Backup")  # uses CRLF newlines
        for sim_path in (sd.sm_path, sd.ssc_path):
            assert sim_path, "Test directory lacks an SM or SSC file"
            sim = simfile.open(sim_path)
            SimfileType = type(sim)
            with self.subTest(SimfileType):
                sim["CUSTOMFIELD"] = "customvalue"
                expected_fragment = dedent_and_trim(
                    """
                    ;\r
                    #CUSTOMFIELD:customvalue;\r
                    \r
                    //---------------dance-single - ranatalus----------------\r
                    #NOTE"""  # NOTES or NOTEDATA
                )
                self.assertIn(expected_fragment, str(sim))
