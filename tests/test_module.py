# coding=utf-8
import os
from typing import List, Set, Type
from msdparser import MSDParserError
from pyfakefs.fake_filesystem_unittest import TestCase  # type: ignore

import simfile
from simfile.sm import SMSimfile
from simfile.ssc import SSCSimfile
from . import test_sm, test_ssc
from simfile.types import Simfile

test_encoding_strings = {
    "utf-8": "μουσικός",
    "cp1252": "música",
    "cp932": "ミュージシャン",
    # It's surprisingly hard to find a CP949 string that's invalid for all the
    # other encodings, which is why this string is nonsense:
    "cp949": "뛃낥",
}


class TestSimfileModuleWithRealFilesystem(TestCase):
    """
    These tests don't work with pyfakefs because FakeFileWrapper instances
    aren't instances of TextIO
    """

    def test_load_blank_sm(self):
        with open("testdata/blank/blank.sm", "r") as reader:
            sm = simfile.load(reader)

        self.assertIsInstance(sm, SMSimfile)

    def test_load_blank_ssc(self):
        with open("testdata/blank/blank.ssc", "r") as reader:
            ssc = simfile.load(reader)

        self.assertIsInstance(ssc, SSCSimfile)


class TestSimfileModule(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory("testdata")

        with open("testing_simfile.sm", "w") as writer:
            writer.write(test_sm.testing_simfile())
        with open("testing_simfile.ssc", "w") as writer:
            writer.write(test_ssc.testing_simfile())
        for encoding, artist in test_encoding_strings.items():
            with open(f"{encoding}.sm", "w", encoding=encoding) as writer:
                writer.write(f"#TITLE:Song;\n#ARTIST:{artist};")
        with open("invalid.sm", "wb") as writer:
            writer.write(b"#TITLE:Song;\n#ARTIST:\xc0\x00\x81;")
        with open("straytext.sm", "wb") as writer:
            writer.write(b"#TITLE:Song;\nSUBTITLE:;\n#ARTIST:Artist;")

    def test_load_with_sm_extension(self):
        with open("testing_simfile.sm", "r") as reader:
            sm = simfile.load(reader)

        self.assertIsInstance(sm, SMSimfile)
        self.assertEqual(SMSimfile(string=test_sm.testing_simfile()), sm)

    def test_load_with_ssc_extension(self):
        with open("testing_simfile.ssc", "r") as reader:
            ssc = simfile.load(reader)

        self.assertIsInstance(ssc, SSCSimfile)
        self.assertEqual(SSCSimfile(string=test_ssc.testing_simfile()), ssc)

    def test_load_with_stray_text(self):
        with open("straytext.sm", "r") as reader:
            self.assertRaises(MSDParserError, simfile.load, reader)

    def test_load_with_stray_text_and_strict_false(self):
        with open("straytext.sm", "r") as reader:
            self.assertEqual("Song", simfile.load(reader, strict=False).title)

    def test_loads_with_sm_contents(self):
        sm = simfile.loads(test_sm.testing_simfile())

        self.assertIsInstance(sm, SMSimfile)
        self.assertEqual(SMSimfile(string=test_sm.testing_simfile()), sm)

    def test_loads_with_ssc_contents(self):
        ssc = simfile.loads(test_ssc.testing_simfile())

        self.assertIsInstance(ssc, SSCSimfile)
        self.assertEqual(SSCSimfile(string=test_ssc.testing_simfile()), ssc)

    def test_loads_with_stray_text(self):
        with open("straytext.sm", "r") as reader:
            straytext = reader.read()

        self.assertRaises(MSDParserError, simfile.loads, straytext)

    def test_loads_with_stray_text_and_strict_false(self):
        with open("straytext.sm", "r") as reader:
            straytext = reader.read()

        self.assertEqual("Song", simfile.loads(straytext, strict=False).title)

    def test_open_with_sm_file(self):
        sm = simfile.open("testing_simfile.sm")

        self.assertIsInstance(sm, SMSimfile)
        self.assertEqual(SMSimfile(string=test_sm.testing_simfile()), sm)

    def test_open_with_ssc_file(self):
        ssc = simfile.open("testing_simfile.ssc")

        self.assertIsInstance(ssc, SSCSimfile)
        self.assertEqual(SSCSimfile(string=test_ssc.testing_simfile()), ssc)

    def test_open_with_non_ascii_encodings(self):
        for encoding, artist in test_encoding_strings.items():
            with self.subTest(encoding):
                sm = simfile.open(f"{encoding}.sm")
                self.assertEqual(artist, sm.artist)

    def test_open_with_invalid_file(self):
        self.assertRaises(UnicodeDecodeError, simfile.open, "invalid.sm")

    def test_open_with_stray_text(self):
        self.assertRaises(MSDParserError, simfile.open, "straytext.sm")

    def test_open_with_stray_text_and_strict_false(self):
        self.assertEqual("Song", simfile.open("straytext.sm", strict=False).title)

    def test_open_with_detected_encoding_with_non_ascii_encodings(self):
        for encoding, artist in test_encoding_strings.items():
            with self.subTest(encoding):
                sm, enc = simfile.open_with_detected_encoding(f"{encoding}.sm")
                self.assertEqual(encoding, enc)
                self.assertEqual(artist, sm.artist)

    def test_open_with_detected_encoding_with_invalid_file(self):
        self.assertRaises(
            UnicodeDecodeError,
            simfile.open_with_detected_encoding,
            "invalid.sm",
        )

    def test_open_with_detected_encoding_with_try_encodings(self):
        sm, enc = simfile.open_with_detected_encoding(f"utf-8.sm", ["utf-8"])
        self.assertEqual("utf-8", enc)
        self.assertEqual(test_encoding_strings["utf-8"], sm.artist)

        self.assertRaises(
            UnicodeDecodeError,
            simfile.open_with_detected_encoding,
            "utf-8.sm",
            ["cp949"],
        )

    def test_open_with_detected_encoding_with_encoding_kwarg(self):
        self.assertRaises(
            TypeError,
            simfile.open_with_detected_encoding,
            "utf-8.sm",
            encoding="cp949",
        )

    def test_open_with_detected_encoding_with_stray_text(self):
        self.assertRaises(
            MSDParserError,
            simfile.open_with_detected_encoding,
            "straytext.sm",
        )

    def test_open_with_detected_encoding_with_stray_text_and_strict_false(self):
        sim, _ = simfile.open_with_detected_encoding(
            "straytext.sm",
            strict=False,
        )
        self.assertEqual("Song", sim.title)

    def test_opendir(self):
        dir = "dir"
        sm_path = os.path.join(dir, "sm_file.sm")
        ssc_path = os.path.join(dir, "ssc_file.ssc")

        os.mkdir(dir)

        sm_file = SMSimfile.blank()
        sm_file.title = "SM"
        with open(sm_path, "w") as writer:
            sm_file.serialize(writer)

        ssc_file = SSCSimfile.blank()
        ssc_file.title = "SSC"
        with open(ssc_path, "w") as writer:
            ssc_file.serialize(writer)

        sim, path = simfile.opendir("dir")
        self.assertEqual(ssc_file, sim)
        self.assertEqual(ssc_path, path)

    def test_openpack(self):
        pack_dir = "My Pack"
        os.mkdir(pack_dir)

        a_dir = os.path.join(pack_dir, "Simfile A")
        os.mkdir(a_dir)
        a_sm_path = os.path.join(a_dir, "a.sm")

        b_dir = os.path.join(pack_dir, "Simfile B")
        os.mkdir(b_dir)
        b_sm_path = os.path.join(b_dir, "b.sm")
        b_ssc_path = os.path.join(b_dir, "b.ssc")

        no_simfile_dir = os.path.join(pack_dir, "tmp")
        os.mkdir(no_simfile_dir)
        no_simfile_file = os.path.join(no_simfile_dir, "tmp.txt")

        for blank_file in (a_sm_path, b_sm_path, b_ssc_path, no_simfile_file):
            with open(blank_file, "w") as writer:
                if blank_file.endswith(".sm"):
                    SMSimfile.blank().serialize(writer)
                if blank_file.endswith(".ssc"):
                    SSCSimfile.blank().serialize(writer)

        sim_types: Set[Type] = set()
        paths: Set[str] = set()
        for sim, path in simfile.openpack(pack_dir):
            sim_types.add(type(sim))
            paths.add(path)

        self.assertEqual(set((SMSimfile, SSCSimfile)), sim_types)
        self.assertEqual(set((a_sm_path, b_ssc_path)), paths)

    def test_mutate_with_sm_file(self):
        with simfile.mutate("testing_simfile.sm") as sm:
            sm["TITLE"] = "Cool Song 2"

        sm = simfile.open("testing_simfile.sm")

        self.assertEqual("Cool Song 2", sm["TITLE"])

    def test_mutate_with_ssc_file(self):
        with simfile.mutate("testing_simfile.ssc") as ssc:
            ssc["TITLE"] = "Cool Song 2"

        ssc = simfile.open("testing_simfile.ssc")

        self.assertEqual("Cool Song 2", ssc["TITLE"])

    def test_mutate_with_output_file(self):
        original_title = None
        modified_title = "Cool Song 2"
        with simfile.mutate(
            "testing_simfile.ssc",
            output_filename="modified.ssc",
        ) as ssc:
            original_title = ssc.title
            ssc.title = modified_title

        ssc = simfile.open("testing_simfile.ssc")
        self.assertEqual(original_title, ssc.title)

        output_ssc = simfile.open("modified.ssc")
        self.assertEqual(modified_title, output_ssc.title)

    def test_mutate_with_backup_file(self):
        original_title = None
        modified_title = "Cool Song 2"
        with simfile.mutate(
            "testing_simfile.ssc",
            backup_filename="backup.ssc",
        ) as ssc:
            original_title = ssc.title
            ssc.title = modified_title

        ssc = simfile.open("testing_simfile.ssc")
        self.assertEqual(modified_title, ssc.title)

        backup_ssc = simfile.open("backup.ssc")
        self.assertEqual(original_title, backup_ssc.title)

    def test_mutate_with_output_and_backup_files(self):
        original_title = None
        modified_title = "Cool Song 2"
        with simfile.mutate(
            "testing_simfile.ssc",
            output_filename="modified.ssc",
            backup_filename="backup.ssc",
        ) as ssc:
            original_title = ssc.title
            ssc.title = modified_title

        ssc = simfile.open("testing_simfile.ssc")
        self.assertEqual(original_title, ssc.title)

        output_ssc = simfile.open("modified.ssc")
        self.assertEqual(modified_title, output_ssc.title)

        backup_ssc = simfile.open("backup.ssc")
        self.assertEqual(original_title, backup_ssc.title)

    def test_mutate_with_invalid_backup_filename(self):
        backup_matches_input = simfile.mutate(
            "testing_simfile.ssc",
            backup_filename="testing_simfile.ssc",
        )
        self.assertRaises(ValueError, backup_matches_input.__enter__)

        backup_matches_output = simfile.mutate(
            "testing_simfile.ssc",
            output_filename="modified.ssc",
            backup_filename="modified.ssc",
        )
        self.assertRaises(ValueError, backup_matches_output.__enter__)

    def test_mutate_with_stray_text_and_strict_true(self):
        self.assertRaises(
            MSDParserError,
            simfile.mutate("straytext.sm", strict=True).__enter__,
        )

    def test_mutate_with_stray_text_and_strict_false(self):
        with simfile.mutate("straytext.sm", strict=False) as straytext:
            straytext.subtitle = "(Fixed)"

        sm = simfile.open("straytext.sm", strict=False)

        self.assertEqual("(Fixed)", sm.subtitle)

    def test_mutate_exactness(self):
        testfiles = (
            "testdata/Backup/backup.sm",
            "testdata/Backup/backup.ssc",
            "testdata/Y.E.A.H/Y.E.A.H.sm",
            "testdata/Y.E.A.H/Y.E.A.H.ssc",
        )
        output_filename = "testdata/output.tmp"
        for testfile in testfiles:
            with self.subTest(testfile=testfile):
                with simfile.mutate(testfile, output_filename=output_filename) as mut:
                    pass
                original_contents = open(testfile).read()
                output_contents = open(output_filename).read()
                self.assertEqual(original_contents, output_contents)
