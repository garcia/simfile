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

        self.assertEqual(ssc_file, sd.simfile)
        self.assertEqual(sm_path, sd.sm)
        self.assertEqual(ssc_path, sd.ssc)
    
    def test_with_sm_only(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        
        os.mkdir(dir)

        sm_file = SMSimfile.blank()
        sm_file.title = 'SM'
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        sd = SimfileDirectory(dir)

        self.assertEqual(sm_file, sd.simfile)
        self.assertEqual(sm_path, sd.sm)
        self.assertIsNone(sd.ssc)
    
    def test_with_ssc_only(self):
        dir = 'dir'
        ssc_path = os.path.join(dir, 'ssc_file.ssc')
        
        os.mkdir(dir)
        
        ssc_file = SSCSimfile.blank()
        ssc_file.title = 'SSC'
        with open(ssc_path, 'w') as writer:
            ssc_file.serialize(writer)
        
        sd = SimfileDirectory(dir)

        self.assertEqual(ssc_file, sd.simfile)
        self.assertIsNone(None, sd.sm)
        self.assertEqual(ssc_path, sd.ssc)
    
    def test_with_no_simfile(self):
        dir = 'dir'        
        os.mkdir(dir)
        self.assertRaises(FileNotFoundError, SimfileDirectory, dir)
    
    def test_inferred_banner(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        bn_path = os.path.join(dir, 'bn.png')
        other_path = os.path.join(dir, 'other.png')
        
        os.mkdir(dir)

        sm_file = SMSimfile.blank()
        sm_file.title = 'SM'
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        with open(bn_path, 'w'): pass
        with open(other_path, 'w'): pass
        
        sd = SimfileDirectory('dir')

        self.assertEqual(sm_file, sd.simfile)
        self.assertEqual(bn_path, sd.banner)
    
    def test_specified_banner(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        bn_path = os.path.join(dir, 'bn.png')
        other_path = os.path.join(dir, 'other.png')
        
        os.mkdir(dir)

        sm_file = SMSimfile.blank()
        sm_file.banner = 'other.png'
        sm_file.title = 'SM'
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        with open(bn_path, 'w'): pass
        with open(other_path, 'w'): pass
        
        sd = SimfileDirectory('dir')

        self.assertEqual(sm_file, sd.simfile)
        self.assertEqual(other_path, sd.banner)