# coding=utf-8
from pyfakefs.fake_filesystem_unittest import TestCase # type: ignore

import simfile
from simfile.sm import SMSimfile
from simfile.ssc import SSCSimfile
from simfile.tests import test_sm, test_ssc

test_encoding_strings = {
    'utf-8': 'μουσικός',
    'cp1252': 'música',
    'cp932': 'ミュージシャン',
    # It's surprisingly hard to find a CP949 string that's invalid for all the
    # other encodings, which is why this string is nonsense:
    'cp949': '뛃낥',
}

class TestSimfileModule(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        with open('testing_simfile.sm', 'w') as writer:
            writer.write(test_sm.testing_simfile())
        with open('testing_simfile.ssc', 'w') as writer:
            writer.write(test_ssc.testing_simfile())
        for encoding, artist in test_encoding_strings.items():
            with open(f'{encoding}.sm', 'w', encoding=encoding) as writer:
                writer.write(f'#TITLE:Song;\n#ARTIST:{artist};')
        with open('invalid.sm', 'wb') as writer:
            writer.write(b'#TITLE:Song;\n#ARTIST:\xc0\x00\x81;')

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
    
    def test_open_with_non_ascii_encodings(self):
        for encoding, artist in test_encoding_strings.items():
            with self.subTest(encoding):
                sm = simfile.open(f'{encoding}.sm')
                self.assertEqual(artist, sm.artist)
    
    def test_open_with_invalid_file(self):
        self.assertRaises(UnicodeDecodeError, simfile.open, 'invalid.sm')
    
    def test_open_with_detected_encoding_with_non_ascii_encodings(self):
        for encoding, artist in test_encoding_strings.items():
            with self.subTest(encoding):
                sm, enc = simfile.open_with_detected_encoding(f'{encoding}.sm')
                self.assertEqual(encoding, enc)
                self.assertEqual(artist, sm.artist)
    
    def test_open_with_detected_encoding_with_invalid_file(self):
        self.assertRaises(
            UnicodeDecodeError,
            simfile.open_with_detected_encoding,
            'invalid.sm',
        )
    
    def test_open_with_detected_encoding_with_try_encodings(self):
        sm, enc = simfile.open_with_detected_encoding(f'utf-8.sm', ['utf-8'])
        self.assertEqual('utf-8', enc)
        self.assertEqual(test_encoding_strings['utf-8'], sm.artist)

        self.assertRaises(
            UnicodeDecodeError,
            simfile.open_with_detected_encoding,
            'utf-8.sm',
            ['cp949'],
        )
    
    def test_open_with_detected_encoding_with_encoding_kwarg(self):
        self.assertRaises(
            TypeError,
            simfile.open_with_detected_encoding,
            'utf-8.sm',
            encoding='cp949',
        )

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
    
    def test_mutate_with_output_file(self):
        original_title = None
        modified_title = 'Cool Song 2'
        with simfile.mutate(
            'testing_simfile.ssc',
            output_filename='modified.ssc',
        ) as ssc:
            original_title = ssc.title
            ssc.title = modified_title
        
        ssc = simfile.open('testing_simfile.ssc')
        self.assertEqual(original_title, ssc.title)

        output_ssc = simfile.open('modified.ssc')
        self.assertEqual(modified_title, output_ssc.title)
    
    def test_mutate_with_backup_file(self):
        original_title = None
        modified_title = 'Cool Song 2'
        with simfile.mutate(
            'testing_simfile.ssc',
            backup_filename='backup.ssc',
        ) as ssc:
            original_title = ssc.title
            ssc.title = modified_title
        
        ssc = simfile.open('testing_simfile.ssc')
        self.assertEqual(modified_title, ssc.title)

        backup_ssc = simfile.open('backup.ssc')
        self.assertEqual(original_title, backup_ssc.title)
    
    def test_mutate_with_output_and_backup_files(self):
        original_title = None
        modified_title = 'Cool Song 2'
        with simfile.mutate(
            'testing_simfile.ssc',
            output_filename='modified.ssc',
            backup_filename='backup.ssc',
        ) as ssc:
            original_title = ssc.title
            ssc.title = modified_title
        
        ssc = simfile.open('testing_simfile.ssc')
        self.assertEqual(original_title, ssc.title)

        output_ssc = simfile.open('modified.ssc')
        self.assertEqual(modified_title, output_ssc.title)

        backup_ssc = simfile.open('backup.ssc')
        self.assertEqual(original_title, backup_ssc.title)
    
    def test_mutate_with_invalid_backup_filename(self):
        backup_matches_input = simfile.mutate(
            'testing_simfile.ssc',
            backup_filename='testing_simfile.ssc',
        )
        self.assertRaises(ValueError, backup_matches_input.__enter__)

        backup_matches_output = simfile.mutate(
            'testing_simfile.ssc',
            output_filename='modified.ssc',
            backup_filename='modified.ssc',
        )
        self.assertRaises(ValueError, backup_matches_output.__enter__)