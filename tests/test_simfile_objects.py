import unittest

import simfile
from simfile._private.dedent import dedent_and_trim
from simfile.dir import SimfileDirectory
from simfile.sm import SMChart, SMSimfile
from simfile.ssc import SSCChart, SSCSimfile
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

    def test_duplicate_keys_preserved(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                maybe_version = "#VERSION:0.83;\n" if sim_type is SSCSimfile else ""

                sim_str = dedent_and_trim(
                    f"""
                    {maybe_version}
                    #TITLE:test;
                    #SUBTITLE:;
                    #ARTIST:;
                    #ATTACKS:line 1;
                    #ATTACKS:line 2;
                    #ATTACKS:line 3;
                    """
                )
                sim = simfile.loads(sim_str)
                self.assertIsInstance(sim, sim_type)

                self.assertEqual("line 1", sim["ATTACKS:1"])
                self.assertEqual("line 2", sim["ATTACKS:2"])
                self.assertEqual("line 3", sim["ATTACKS"])
                self.assertEqual(sim.attacks, "line 3")
                self.assertEqual(
                    [
                        *(["VERSION"] if maybe_version else []),
                        "TITLE",
                        "SUBTITLE",
                        "ARTIST",
                        "ATTACKS:1",
                        "ATTACKS:2",
                        "ATTACKS",
                    ],
                    list(sim.keys()),
                )

                stringified = str(sim)
                self.assertEqual(sim_str, stringified)
                self.assertEqual(sim, simfile.loads(stringified))

    def test_key_case_preserved(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                maybe_version = "#Version:0.83;\n" if sim_type is SSCSimfile else ""

                sim_str = dedent_and_trim(
                    f"""
                    {maybe_version}
                    #title:test;
                    #SUBTITLE:;
                    #ARTIST:;
                    #ATTACKS:line 1;
                    #Attacks:line 2;
                    #attacks:line 3;
                    """
                )
                sim = simfile.loads(sim_str)
                self.assertIsInstance(sim, sim_type)

                self.assertEqual("test", sim.title)
                self.assertEqual("line 1", sim["ATTACKS:1"])
                self.assertEqual("line 2", sim["ATTACKS:2"])
                self.assertEqual("line 3", sim["ATTACKS"])
                self.assertEqual(sim.attacks, "line 3")
                self.assertEqual(
                    [
                        *(["VERSION"] if maybe_version else []),
                        "TITLE",
                        "SUBTITLE",
                        "ARTIST",
                        "ATTACKS:1",
                        "ATTACKS:2",
                        "ATTACKS",
                    ],
                    list(sim.keys()),
                )

                stringified = str(sim)
                self.assertEqual(sim_str, stringified)
                self.assertEqual(sim, simfile.loads(stringified))

    def test_changing_value_resets_ephemera(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                maybe_version = "#VERSION:0.83;\n" if sim_type is SSCSimfile else ""

                sim_str = dedent_and_trim(
                    f"""
                    {maybe_version}
                    #TITLE:\\#Fairy_dancing_in_lake// test
                    ;
                    #SUBTITLE:;
                    #ARTIST:;
                    #ATTACKS:line 1;
                    #ATTACKS:line 2;
                    #ATTACKS:line 3;
                    """
                )
                sim = simfile.loads(sim_str)
                self.assertIsInstance(sim, sim_type)

                self.assertIn("#TITLE:\\#Fairy_dancing_in_lake// test\n;\n", str(sim))

                sim.title = "something else"

                self.assertIn("#TITLE:something else;\n", str(sim))

    def test_changing_value_in_sm_chart_resets_ephemera(self):
        sim_str = dedent_and_trim(
            """
            #NOTES:
                    dance-single:
                    http\\:\\//stepartist.example:
                    Beginner:
                    1:
                    0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            // measure 0
            0000
            0000
            0000
            0000
            ;
            """
        )
        expected = dedent_and_trim(
            """
            #NOTES:
                    dance-single:
                    A more normal description:
                    Beginner:
                    1:
                    0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            
            0000
            0000
            0000
            0000
            ;
            """
        )

        sim = simfile.loads(sim_str)
        sim.charts[0].description = "A more normal description"

        self.assertEqual(expected, str(sim))
