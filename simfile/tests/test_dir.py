import os

from pyfakefs.fake_filesystem_unittest import TestCase # type: ignore
from simfile.dir import SimfileDirectory

from simfile.sm import SMSimfile
from simfile.ssc import SSCSimfile


class TestSimfileDirectory(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_with_sm_and_ssc(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        ssc_path = os.path.join(dir, 'ssc_file.ssc')
        
        os.mkdir(dir)

        sm_file = SMSimfile.blank()
        sm_file.title = 'SM'
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        ssc_file = SSCSimfile.blank()
        ssc_file.title = 'SSC'
        with open(ssc_path, 'w') as writer:
            ssc_file.serialize(writer)
        
        sd = SimfileDirectory('dir')

        self.assertEqual(sm_path, sd.sm_path)
        self.assertEqual(ssc_path, sd.ssc_path)
        self.assertEqual(ssc_file, sd.open())
    
    def test_with_sm_only(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        
        os.mkdir(dir)

        sm_file = SMSimfile.blank()
        sm_file.title = 'SM'
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        sd = SimfileDirectory(dir)

        self.assertEqual(sm_path, sd.sm_path)
        self.assertIsNone(sd.ssc_path)
        self.assertEqual(sm_file, sd.open())
    
    def test_with_ssc_only(self):
        dir = 'dir'
        ssc_path = os.path.join(dir, 'ssc_file.ssc')
        
        os.mkdir(dir)
        
        ssc_file = SSCSimfile.blank()
        ssc_file.title = 'SSC'
        with open(ssc_path, 'w') as writer:
            ssc_file.serialize(writer)
        
        sd = SimfileDirectory(dir)

        self.assertIsNone(sd.sm_path)
        self.assertEqual(ssc_path, sd.ssc_path)
        self.assertEqual(ssc_file, sd.open())
    
    def test_with_no_simfile(self):
        dir = 'dir'        
        os.mkdir(dir)
        sd = SimfileDirectory(dir)
        
        self.assertIsNone(sd.sm_path)
        self.assertIsNone(sd.ssc_path)
        self.assertRaises(FileNotFoundError, sd.open)
