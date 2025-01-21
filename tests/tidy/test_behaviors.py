from collections import OrderedDict
from dataclasses import replace
import functools
import itertools
import operator
import unittest

import simfile
from simfile.sm import AttachedSMChart, SMChart, SMSimfile
from simfile.ssc import SSCSimfile
from simfile.tidy import tidy
from simfile._private.dedent import dedent_and_trim
from simfile.tidy.behaviors import (
    CreateComments,
    CreateMissingProperties,
    DestructivelyRemoveProperties,
    LineEndings,
    Preset,
    RemoveComments,
    SortProperties,
    Whitespace,
)
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


class TestPresets(SimfileTestCase):
    sm_string = dedent_and_trim(
        """
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;
            #TITLETRANSLIT:;\r
            #SUBTITLETRANSLIT:;\r
                #ARTISTTRANSLIT:;\r

            #UNKNOWN:field;
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

    def test_no_op_preset(self):
        sim = simfile.loads(self.sm_string)
        self.assertFalse(tidy(sim, Preset.NO_OP))

    def test_sm5_preset(self):
        sim = simfile.loads(self.sm_string)
        expected = dedent_and_trim(
            """
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;
            #TITLETRANSLIT:;
            #SUBTITLETRANSLIT:;
            #ARTISTTRANSLIT:;
            #GENRE:;
            #CREDIT:;
            #BANNER:;
            #BACKGROUND:;
            #LYRICSPATH:;
            #CDTITLE:;
            #MUSIC:;
            #OFFSET:0.000000;
            #SAMPLESTART:100.000000;
            #SAMPLELENGTH:12.000000;
            #SELECTABLE:YES;
            #BPMS:0.000000=60.000000;
            #STOPS:;
            #BGCHANGES:;
            #KEYSOUNDS:;
            #ATTACKS:;
            #UNKNOWN:field;

            //---------------dance-single - http://stepartist.example----------------
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

            //---------------dance-single - ----------------
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
            ,  // measure 1
            0100
            0010
            1000
            0001
            ;
            """
        )

        self.assertTrue(tidy(sim, Preset.SM5))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check:
        # TODO(ash): fix Create/RemoveComments clobbering idempotency flag
        # self.assertFalse(tidy(sim, Preset.SM5))

    def test_sm5_destructive_preset(self):
        sim = simfile.loads(self.sm_string)
        expected = dedent_and_trim(
            """
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;
            #TITLETRANSLIT:;
            #SUBTITLETRANSLIT:;
            #ARTISTTRANSLIT:;
            #GENRE:;
            #CREDIT:;
            #BANNER:;
            #BACKGROUND:;
            #LYRICSPATH:;
            #CDTITLE:;
            #MUSIC:;
            #OFFSET:0.000000;
            #SAMPLESTART:100.000000;
            #SAMPLELENGTH:12.000000;
            #SELECTABLE:YES;
            #BPMS:0.000000=60.000000;
            #STOPS:;
            #BGCHANGES:;
            #KEYSOUNDS:;
            #ATTACKS:;

            //---------------dance-single - http://stepartist.example----------------
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

            //---------------dance-single - ----------------
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
            ,  // measure 1
            0100
            0010
            1000
            0001
            ;
            """
        )

        self.assertTrue(tidy(sim, Preset.SM5_DESTRUCTIVE))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check:
        # TODO(ash): fix Create/RemoveComments clobbering idempotency flag
        # self.assertFalse(tidy(sim, Preset.SM5))

    def test_recommended_preset(self):
        sim = simfile.loads(self.sm_string)
        expected = dedent_and_trim(
            f"""
            // Generated by simfile {simfile.__version__} for Python
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;
            #TITLETRANSLIT:;
            #SUBTITLETRANSLIT:;
            #ARTISTTRANSLIT:;
            #GENRE:;
            #CREDIT:;
            #BANNER:;
            #BACKGROUND:;
            #LYRICSPATH:;
            #CDTITLE:;
            #MUSIC:;
            #OFFSET:0.000000;
            #SAMPLESTART:100.000000;
            #SAMPLELENGTH:12.000000;
            #SELECTABLE:YES;
            #BPMS:0.000000=60.000000;
            #STOPS:;
            #BGCHANGES:;
            #KEYSOUNDS:;
            #ATTACKS:;
            #UNKNOWN:field;

            //---------------dance-single - http://stepartist.example----------------
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

            //---------------dance-single - ----------------
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
            ,  // measure 1
            0100
            0010
            1000
            0001
            ;
            """
        )

        self.assertTrue(tidy(sim, Preset.RECOMMENDED))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check:
        # TODO(ash): fix Create/RemoveComments clobbering idempotency flag
        # self.assertFalse(tidy(sim, Preset.SM5))


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
        # Subtract 1 from the exponent to ignore RemoveComments.ALL
        # and 1 from the result to ignore the empty combination
        self.assertEqual(2 ** (len(RemoveComments) - 1) - 1, permutation_count)


class TestCreateComments(SimfileTestCase):
    def maybe_version(self, sim_type: type[SMSimfile] | type[SSCSimfile]):
        return "#VERSION:0.83;\n" if sim_type is SSCSimfile else ""

    def test_library_version_preamble_already_exists_at_top(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                sim = simfile.loads(
                    dedent_and_trim(
                        f"""
                        // Generated by simfile {simfile.__version__} for Python
                        // Another preamble comment
                        {self.maybe_version(sim_type)}
                        #TITLE:test;
                        #SUBTITLE:;
                        #ARTIST:;
                        """
                    ).replace("\n\n", "\n")
                )

                self.assertFalse(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )

    def test_library_version_preamble_updated_at_top(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                sim = simfile.loads(
                    dedent_and_trim(
                        f"""
                        // Generated by simfile 3.0.0-dummy for Python
                        // Another preamble comment
                        {self.maybe_version(sim_type)}
                        #TITLE:test;
                        #SUBTITLE:;
                        #ARTIST:;
                        """
                    ).replace("\n\n", "\n")
                )
                expected = str(sim).replace("3.0.0-dummy", simfile.__version__)

                self.assertTrue(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )
                self.assertEqual(expected, str(sim))

                # Validity check
                self.assertEqual(sim, simfile.loads(str(sim)))

                # Idempotency check
                self.assertFalse(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )

    def test_library_version_preamble_updated_at_bottom(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                sim = simfile.loads(
                    dedent_and_trim(
                        f"""
                        // Preamble comment
                        // Generated by simfile 3.0.0-dummy for Python
                        {self.maybe_version(sim_type)}
                        #TITLE:test;
                        #SUBTITLE:;
                        #ARTIST:;
                        """
                    ).replace("\n\n", "\n")
                )
                expected = str(sim).replace("3.0.0-dummy", simfile.__version__)

                self.assertTrue(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )
                self.assertEqual(expected, str(sim))

                # Validity check
                self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

                # Idempotency check
                self.assertFalse(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )

    def test_library_version_preamble_added_after_existing_preamble(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                sim = simfile.loads(
                    dedent_and_trim(
                        f"""
                        // Preamble comment
                        {self.maybe_version(sim_type)}
                        #TITLE:test;
                        #SUBTITLE:;
                        #ARTIST:;
                        """
                    ).replace("\n\n", "\n")
                )
                expected = dedent_and_trim(
                    f"""
                    // Preamble comment
                    // Generated by simfile {simfile.__version__} for Python
                    {self.maybe_version(sim_type)}
                    #TITLE:test;
                    #SUBTITLE:;
                    #ARTIST:;
                    """
                ).replace("\n\n", "\n")

                self.assertTrue(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )
                self.assertEqual(expected, str(sim))

                # Validity check
                self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

                # Idempotency check
                self.assertFalse(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )

    def test_library_version_preamble_added_without_existing_preamble(self):
        for sim_type in (SMSimfile, SSCSimfile):
            with self.subTest(sim_type):
                sim = simfile.loads(
                    dedent_and_trim(
                        f"""
                        {self.maybe_version(sim_type)}
                        #TITLE:test;
                        #SUBTITLE:;
                        #ARTIST:;
                        """
                    ).lstrip()
                )
                expected = (  # comment to force line break
                    f"// Generated by simfile {simfile.__version__} for Python\n"
                    + str(sim)
                )

                self.assertTrue(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )
                self.assertEqual(expected, str(sim))

                # Validity check
                self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

                # Idempotency check
                self.assertFalse(
                    tidy(sim, create_comments=CreateComments.LIBRARY_VERSION_PREAMBLE)
                )

    def test_sm_chart_preamble_added_without_existing_preamble(self):
        sim = simfile.loads(
            dedent_and_trim(
                f"""
                #TITLE:test;
                #SUBTITLE:;
                #ARTIST:;

                #NOTES:
                        dance-single:
                        authorname:
                        Beginner:
                        1:
                        0.000,0.000,0.000,0.000,0.000:
                // measure 0
                0000
                0000
                0000
                0000
                ;
                """
            ).lstrip()
        )
        expected = str(sim).replace(
            "#NOTES:\n",
            "//---------------dance-single - authorname----------------\n#NOTES:\n",
        )

        self.assertTrue(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))

    def test_sm_chart_preamble_already_exists(self):
        sim = simfile.loads(
            dedent_and_trim(
                f"""
                #TITLE:test;
                #SUBTITLE:;
                #ARTIST:;

                //---------------dance-single - authorname----------------
                #NOTES:
                        dance-single:
                        authorname:
                        Beginner:
                        1:
                        0.000,0.000,0.000,0.000,0.000:
                // measure 0
                0000
                0000
                0000
                0000
                ;
                """
            ).lstrip()
        )

        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))

    def test_sm_chart_preamble_updated(self):
        sim = simfile.loads(
            dedent_and_trim(
                f"""
                #TITLE:test;
                #SUBTITLE:;
                #ARTIST:;

                //---------------dance-single - ----------------
                #NOTES:
                        dance-single:
                        authorname:
                        Beginner:
                        1:
                        0.000,0.000,0.000,0.000,0.000:
                // measure 0
                0000
                0000
                0000
                0000
                ;
                """
            ).lstrip()
        )
        expected = str(sim).replace(
            "//---------------dance-single - ----------------\n",
            "//---------------dance-single - authorname----------------\n",
        )

        self.assertTrue(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))

    def test_ssc_chart_preamble_added_without_existing_preamble(self):
        sim = simfile.loads(
            dedent_and_trim(
                f"""
                #VERSION:0.83;
                #TITLE:test;
                #SUBTITLE:;
                #ARTIST:;

                #NOTEDATA:;
                #STEPSTYPE:dance-single;
                #DESCRIPTION:authorname;
                #DIFFICULTY:Beginner;
                #METER:1;
                #RADARVALUES:0.000,0.000,0.000,0.000,0.000;
                #NOTES:
                // measure 0
                0000
                0000
                0000
                0000
                ;
                """
            ).lstrip()
        )
        expected = str(sim).replace(
            "#NOTEDATA:;\n",
            "//---------------dance-single - authorname----------------\n#NOTEDATA:;\n",
        )

        self.assertTrue(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))

    def test_ssc_chart_preamble_already_exists(self):
        sim = simfile.loads(
            dedent_and_trim(
                f"""
                #VERSION:0.83;
                #TITLE:test;
                #SUBTITLE:;
                #ARTIST:;

                //---------------dance-single - authorname----------------
                #NOTEDATA:;
                #STEPSTYPE:dance-single;
                #DESCRIPTION:authorname;
                #DIFFICULTY:Beginner;
                #METER:1;
                #RADARVALUES:0.000,0.000,0.000,0.000,0.000;
                #NOTES:
                // measure 0
                0000
                0000
                0000
                0000
                ;
                """
            ).lstrip()
        )

        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))

    def test_ssc_chart_preamble_updated(self):
        sim = simfile.loads(
            dedent_and_trim(
                f"""
                #VERSION:0.83;
                #TITLE:test;
                #SUBTITLE:;
                #ARTIST:;

                //---------------dance-single - ----------------
                #NOTEDATA:;
                #STEPSTYPE:dance-single;
                #DESCRIPTION:authorname;
                #DIFFICULTY:Beginner;
                #METER:1;
                #RADARVALUES:0.000,0.000,0.000,0.000,0.000;
                #NOTES:
                // measure 0
                0000
                0000
                0000
                0000
                ;
                """
            ).lstrip()
        )
        expected = str(sim).replace(
            "//---------------dance-single - ----------------\n",
            "//---------------dance-single - authorname----------------\n",
        )

        self.assertTrue(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))
        self.assertEqual(expected, str(sim))

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_PREAMBLE))

    def test_sm_chart_measures_already_exist(self):
        sim = simfile.open("testdata/backup/backup.sm")
        assert isinstance(sim, SMSimfile)

        # Pare down charts to just the one that has measure comments
        chart = next(
            filter(
                lambda chart: chart.stepstype == "dance-single"
                and chart.difficulty == "Challenge",
                sim.charts,
            )
        )
        sim.charts.clear()
        sim.charts.append(chart)

        original = simfile.loads(str(sim))

        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_MEASURES))

        self.assertSimfilesEqual(original, sim)

    def test_sm_chart_measures_added_without_existing_chart_measures(self):
        sim = simfile.open("testdata/backup/backup.sm")
        assert isinstance(sim, SMSimfile)

        # Pare down charts to just one that doesn't have measure comments
        chart = next(
            filter(
                lambda chart: chart.stepstype == "dance-single"
                and chart.difficulty == "Beginner",
                sim.charts,
            )
        )
        sim.charts.clear()
        sim.charts.append(chart)

        self.assertTrue(tidy(sim, create_comments=CreateComments.CHART_MEASURES))
        mn = 0
        for line in str(sim.charts[0]).splitlines():
            if mn == 0 and line.lstrip().startswith("// "):
                self.assertEqual("// measure 0", line)
                mn += 1
            elif line.startswith(","):
                self.assertEqual(f",  // measure {mn}", line)
                mn += 1

    def test_ssc_chart_measures_already_exist(self):
        sim = simfile.open("testdata/backup/backup.ssc")
        assert isinstance(sim, SSCSimfile)

        # Pare down charts to just the one that has measure comments
        chart = next(
            filter(
                lambda chart: chart.stepstype == "dance-single"
                and chart.difficulty == "Challenge",
                sim.charts,
            )
        )
        sim.charts.clear()
        sim.charts.append(chart)

        self.assertFalse(tidy(sim, create_comments=CreateComments.CHART_MEASURES))

    def test_ssc_chart_measures_added_without_existing_chart_measures(self):
        sim = simfile.open("testdata/backup/backup.ssc")
        assert isinstance(sim, SSCSimfile)

        # Pare down charts to just one that doesn't have measure comments
        chart = next(
            filter(
                lambda chart: chart.stepstype == "dance-single"
                and chart.difficulty == "Beginner",
                sim.charts,
            )
        )
        sim.charts.clear()
        sim.charts.append(chart)

        self.assertTrue(tidy(sim, create_comments=CreateComments.CHART_MEASURES))
        mn = 0
        for line in str(sim.charts[0]).splitlines():
            if mn == 0 and line.lstrip().startswith("// "):
                self.assertEqual("// measure 0", line)
                mn += 1
            elif line.startswith(","):
                self.assertEqual(f",  // measure {mn}", line)
                mn += 1


class TestCreateMissingProperties(SimfileTestCase):
    def test_sm5_sm_no_missing_properties(self):
        sim = simfile.open("testdata/backup/backup.sm")

        self.assertFalse(
            tidy(sim, create_missing_properties=CreateMissingProperties.SM5)
        )

    def test_sm5_sm_create_missing_properties(self):
        sim = SMSimfile()
        sim.title = "test"

        self.assertTrue(
            tidy(sim, create_missing_properties=CreateMissingProperties.SM5)
        )

        self.assertEqual("test", sim.title)
        self.assertEqual("", sim.subtitle)
        self.assertEqual(SMSimfile.blank().offset, sim.offset)
        # Not a default property (only present if specified):
        self.assertIsNone(sim.displaybpm)

    def test_sm5_ssc_no_missing_properties(self):
        sim = simfile.open("testdata/backup/backup.sm")

        self.assertFalse(
            tidy(sim, create_missing_properties=CreateMissingProperties.SM5)
        )

    def test_sm5_ssc_chart_missing_timing_properties(self):
        sim = simfile.open("testdata/backup/backup.ssc")
        assert isinstance(sim, SSCSimfile)

        chart = sim.charts[0]
        chart.offset = "0.000"

        self.assertTrue(
            tidy(sim, create_missing_properties=CreateMissingProperties.SM5)
        )

        self.assertEqual("0.000", chart.offset)
        self.assertEqual("0.000=60.000", chart.bpms)
        self.assertEqual("", chart.warps)

    def test_sm5_ssc_simfile_missing_properties(self):
        sim = SSCSimfile()
        sim.title = "test"

        self.assertTrue(
            tidy(sim, create_missing_properties=CreateMissingProperties.SM5)
        )

        self.assertEqual("test", sim.title)
        self.assertEqual("", sim.subtitle)
        self.assertEqual(SSCSimfile.blank().offset, sim.offset)
        # SSC-specific property:
        self.assertEqual(SSCSimfile.blank().labels, sim.labels)
        # Not a default property (only present if specified):
        self.assertIsNone(sim.displaybpm)


class TestDestructivelyRemoveProperties(SimfileTestCase):
    def test_sm5_no_unknown_properties(self):
        sim = simfile.open("testdata/backup/backup.sm")
        self.assertFalse(
            tidy(sim, destructively_remove_properties=DestructivelyRemoveProperties.SM5)
        )

        sim = simfile.open("testdata/backup/backup.ssc")
        self.assertFalse(
            tidy(sim, destructively_remove_properties=DestructivelyRemoveProperties.SM5)
        )

    def test_sm5_sm_unknown_properties(self):
        sim = simfile.open("testdata/backup/backup.sm")
        sim["FOO"] = "bar"
        self.assertTrue(
            tidy(sim, destructively_remove_properties=DestructivelyRemoveProperties.SM5)
        )
        assert "FOO" not in sim

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(
            tidy(sim, destructively_remove_properties=DestructivelyRemoveProperties.SM5)
        )

    def test_sm5_ssc_unknown_properties(self):
        sim = simfile.open("testdata/backup/backup.ssc")
        sim["FOO"] = "bar"
        self.assertTrue(
            tidy(sim, destructively_remove_properties=DestructivelyRemoveProperties.SM5)
        )
        assert "FOO" not in sim

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(
            tidy(sim, destructively_remove_properties=DestructivelyRemoveProperties.SM5)
        )


class TestSortProperties(SimfileTestCase):
    def test_already_sorted(self):
        sim = simfile.open("testdata/backup/backup.sm")
        self.assertFalse(tidy(sim, sort_properties=SortProperties.SM5))

        sim = simfile.open("testdata/backup/backup.ssc")
        self.assertFalse(tidy(sim, sort_properties=SortProperties.SM5))

    def test_already_sorted_with_unknown_props(self):
        sim = simfile.open("testdata/backup/backup.sm")
        sim["UNKNOWN1"] = "foo"
        sim["UNKNOWN2"] = "bar"
        self.assertFalse(tidy(sim, sort_properties=SortProperties.SM5))

    def test_only_unknown_props_unsorted(self):
        sim = simfile.open("testdata/backup/backup.sm")
        sim["UNKNOWN2"] = "bar"
        sim["UNKNOWN1"] = "foo"
        original_keys = [*sim.keys()]

        self.assertTrue(tidy(sim, sort_properties=SortProperties.SM5))

        self.assertEqual([*sim.keys()], original_keys[:-2] + ["UNKNOWN1", "UNKNOWN2"])

        # Validity check
        self.assertSimfilesEqual(sim, simfile.loads(str(sim)))

        # Idempotency check
        self.assertFalse(tidy(sim, sort_properties=SortProperties.SM5))

    def test_reversed(self):
        sim = simfile.open("testdata/backup/backup.sm")
        first_prop = next(iter(sim._properties.values()))
        first_prop.msd_parameter = replace(first_prop.msd_parameter, preamble=None)
        original_contents = str(sim)
        sim._properties = OrderedDict(reversed(sim._properties.items()))
        self.assertEqual("ATTACKS", next(iter(sim._properties.keys())))

        self.assertTrue(tidy(sim, sort_properties=SortProperties.SM5))

        self.assertEqual(str(sim), original_contents)

        # Idempotency check
        self.assertFalse(tidy(sim, sort_properties=SortProperties.SM5))
