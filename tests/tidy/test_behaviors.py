from dataclasses import replace
import functools
import itertools
import operator
import unittest
import simfile
from simfile.sm import SMChart
from simfile.tidy import tidy
from simfile._private.dedent import dedent_and_trim
from simfile.tidy.behaviors import LineEndings, RemoveComments, Whitespace
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


class TestRemoveComments(SimfileTestCase):
    def sm_test_file(self):
        return simfile.loads(
            dedent_and_trim(
                """
            // Simfile preamble
            #TITLE:Song title; // Simfile suffix
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;
            #BPMS: // Simfile inner
            0.000=120.000
            ;

            // Chart preamble
            #NOTES:
                 dance-single: // Chart inner
                 Beginner:
                 :
                 1:
                 0.000,0.000,0.000,0.000,0.000:
            // Chart inner
            1000
            0100
            0010
            0001
            , // Chart inner
            0100
            0010
            1000
            0001
            ; // Chart suffix
            """
            )
        )

    def ssc_test_file(self):
        return simfile.loads(
            dedent_and_trim(
                """
            // Simfile preamble
            #VERSION:0.83; // Simfile suffix
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;
            #BPMS: // Simfile inner
            0.000=120.000
            ;

            // Chart preamble
            #NOTEDATA:// Chart inner
            ; // Chart suffix
            #STEPSTYPE:dance-single;
            #DIFFICULTY:Beginner;
            #METER:1;
            #NOTES:
            // Chart inner
            1000
            0100
            0010
            0001
            , // Chart inner
            0100
            0010
            1000
            0001
            ; // Chart suffix
            """
            )
        )

    def naively_remove_comments(
        self, original: str, remove_comments: RemoveComments
    ) -> str:
        result = original
        if RemoveComments.PREAMBLE in remove_comments:
            result = result.replace("// Simfile preamble\n", "")
        if RemoveComments.CHART_PREAMBLE in remove_comments:
            result = result.replace("// Chart preamble\n", "")
        if RemoveComments.CHART_INNER in remove_comments:
            result = result.replace("// Chart inner", "")
            result = result.replace("// Chart inner", "")
        if RemoveComments.OTHER in remove_comments:
            result = result.replace("// Simfile inner", "")
            result = result.replace("// Simfile suffix", "")
            result = result.replace("// Chart suffix", "")
            result = result.replace("// Chart suffix", "")

        return result

    def test_permutations(self):
        permutation_count = 0
        seen_outputs: set[str] = set()

        for combination in itertools.product(
            (RemoveComments(0), RemoveComments.PREAMBLE),
            (RemoveComments(0), RemoveComments.CHART_PREAMBLE),
            (RemoveComments(0), RemoveComments.CHART_INNER),
            (RemoveComments(0), RemoveComments.OTHER),
        ):
            remove_comments = functools.reduce(
                operator.or_, combination, RemoveComments(0)
            )
            if not remove_comments:
                continue

            permutation_count += 1

            for test_file in (self.sm_test_file(), self.ssc_test_file()):
                with self.subTest((combination, type(test_file))):
                    original = str(test_file)

                    self.assertTrue(tidy(test_file, remove_comments=remove_comments))

                    self.assertEqual(
                        self.naively_remove_comments(original, remove_comments),
                        str(test_file),
                    )

                    # Ensure every combination of flags yields unique output;
                    # otherwise, the test file probably isn't granular enough
                    output = str(test_file)
                    if output in seen_outputs:
                        self.fail(f"already saw this output:\n{output}")
                    seen_outputs.add(output)

                    # Validity check
                    self.assertSimfilesEqual(test_file, simfile.loads(output))
                    # Idempotency check
                    self.assertFalse(tidy(test_file, remove_comments=remove_comments))

        # Ensure we got all the expected combinations;
        # otherwise, the combinations may not be exhaustive
        self.assertEqual(2 ** len(RemoveComments) - 1, permutation_count)
