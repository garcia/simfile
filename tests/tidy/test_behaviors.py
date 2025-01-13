from dataclasses import replace
import unittest
import simfile
from simfile.sm import SMChart
from simfile.tidy import tidy
from simfile._private.dedent import dedent_and_trim
from simfile.tidy.behaviors import LineEndings, Whitespace
from simfile.types import Simfile


class SimfileTestCase(unittest.TestCase):
    def assertSimfilesEqual(self, a: Simfile, b: Simfile):
        self.maxDiff = None
        self.assertEqual(type(a), type(b))
        self.assertDictEqual(a._properties, b._properties)
        self.assertEqual(a._default_parameter, b._default_parameter)

        for ca, cb in zip(a.charts, b.charts):
            self.assertEqual(type(ca), type(cb))
            self.assertDictEqual(ca._properties, cb._properties)
            # if isinstance(ca, SMChart) and isinstance(cb, SMChart):
            #     self.assertEqual(ca._real_parameter, cb._real_parameter)

        self.assertEqual(a, b)


class TestWhitespace(SimfileTestCase):
    def test_sm5_sm(self):
        self.maxDiff = None
        sim_string = dedent_and_trim(
            """
            #TITLE:Song title;#SUBTITLE:Song subtitle;
                        
                #ARTIST:Song artist;
            #NOTES:
            dance-single:

            http\\:\\//stepartist.example: // contrived use of escapes
            Beginner:
            1:
            0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000;
            // comment
                        #NOTES:
                 dance-single:
                 :
                 Easy:
                 3:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment SM"""
        )

        expected = dedent_and_trim(
            """
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;

            #NOTES:
                 dance-single:
                 http\\:\\//stepartist.example:
                 Beginner:
                 1:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000
            ;

            // comment
            #NOTES:
                 dance-single:
                 :
                 Easy:
                 3:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment SM
            """
        )

        sim = simfile.loads(sim_string)
        self.assertTrue(tidy(sim, whitespace=Whitespace.SM5))
        self.assertEqual(expected, str(sim))
        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))
        # Idempotency check
        self.assertFalse(tidy(sim, whitespace=Whitespace.SM5))

    def test_sm5_ssc(self):
        self.maxDiff = None
        sim_string = dedent_and_trim(
            """
            #VERSION:0.83;
            #TITLE:Song title;#SUBTITLE:Song subtitle;
                        
                #ARTIST:Song artist;
            #NOTEDATA:;
            #STEPSTYPE:dance-single;#DIFFICULTY:Beginner;
            #METER:1;

            #CREDIT:http\\:\\//stepartist.example; // contrived use of escapes

            #NOTES:
            0000
            0000
            0000
            0000
            ;
            // comment

            
            #NOTEDATA:;
            #STEPSTYPE:dance-single;#DIFFICULTY:Easy;
            
            #METER:3;
            #NOTES:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment"""
        )
        expected = dedent_and_trim(
            """
            #VERSION:0.83;
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;

            #NOTEDATA:;
            #STEPSTYPE:dance-single;
            #DIFFICULTY:Beginner;
            #METER:1;
            #CREDIT:http\\:\\//stepartist.example; // contrived use of escapes
            #NOTES:
            0000
            0000
            0000
            0000
            ;

            // comment
            #NOTEDATA:;
            #STEPSTYPE:dance-single;
            #DIFFICULTY:Easy;
            #METER:3;
            #NOTES:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment
            """
        )

        sim = simfile.loads(sim_string)
        self.assertTrue(tidy(sim, whitespace=Whitespace.SM5))
        self.assertEqual(expected, str(sim))
        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))
        # Idempotency check
        self.assertFalse(tidy(sim, whitespace=Whitespace.SM5))


class TestLineEndings(SimfileTestCase):
    TEST_FILES = (
        # CRLF
        ("\r\n", "testdata/Backup/backup.sm"),
        ("\r\n", "testdata/Backup/backup.ssc"),
        # LF
        ("\n", "testdata/nekonabe/nekonabe.sm"),
        ("\n", "testdata/spin_cycle/spin_cycle.ssc"),
    )

    def test_lf(self):
        for nl, filename in TestLineEndings.TEST_FILES:
            sim = simfile.open(filename)
            with self.subTest(filename):
                result = tidy(sim, line_endings=LineEndings.LF)
                if nl == "\n":
                    self.assertFalse(
                        result, "simfile unexpectedly flagged as unchanged"
                    )
                else:
                    self.assertTrue(result, "simfile unexpectedly flagged as changed")

                for i, line in enumerate(str(sim).splitlines(keepends=True)):
                    self.assertFalse(
                        line.endswith("\r\n"), f"line {i} missed: {repr(line)}"
                    )
                    self.assertTrue(
                        line.endswith("\n"), f"line {i} incorrect: {repr(line)}"
                    )

                # Validity check
                self.assertSimfilesEqual(sim, simfile.loads(str(sim)))
                # Idempotency check
                self.assertFalse(tidy(sim, line_endings=LineEndings.LF))

    def test_crlf(self):
        for nl, filename in TestLineEndings.TEST_FILES:
            sim = simfile.open(filename)
            with self.subTest(filename):
                result = tidy(sim, line_endings=LineEndings.CRLF)
                if nl == "\r\n":
                    self.assertFalse(
                        result, "simfile unexpectedly flagged as unchanged"
                    )
                else:
                    self.assertTrue(result, "simfile unexpectedly flagged as changed")

                for i, line in enumerate(str(sim).splitlines(keepends=True)):
                    self.assertTrue(
                        line.endswith("\r\n"), f"line {i} missed: {repr(line)}"
                    )

                # Validity check
                self.assertSimfilesEqual(sim, simfile.loads(str(sim)))
                # Idempotency check
                self.assertFalse(tidy(sim, line_endings=LineEndings.CRLF))

    def test_heuristic(self):
        for nl, filename in TestLineEndings.TEST_FILES:
            sim = simfile.open(filename)
            with self.subTest(filename):
                # All of the test files have consistent newlines
                self.assertFalse(tidy(sim, line_endings=LineEndings.HEURISTIC))

                # Validity check
                self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

                # Let's try denormalizing a newline:
                sim._properties["TITLE"].msd_parameter = replace(
                    sim._properties["TITLE"].msd_parameter,
                    suffix=";\r\n" if nl == "\n" else ";\n",
                )
                self.assertTrue(tidy(sim, line_endings=LineEndings.HEURISTIC))
                self.assertEqual(
                    sim._properties["TITLE"].msd_parameter.suffix, f";{nl}"
                )
