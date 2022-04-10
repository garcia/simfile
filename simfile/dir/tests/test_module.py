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
    
    ASSET_PATHS = {
        'BANNER': {
            'property': SimfileDirectory.banner,
            'predefined': 'bn.png',
            'specified': '1.png',
        },
        'BACKGROUND': {
            'property': SimfileDirectory.background,
            'predefined': 'bg.png',
            'specified': '2.png',
        },
        'CDTITLE': {
            'property': SimfileDirectory.cdtitle,
            'predefined': 'cdtitle.png',
            'specified': '3.png',
        },
        'JACKET': {
            'property': SimfileDirectory.jacket,
            'predefined': 'jacket.png',
            'specified': '4.png',
        },
        'CDIMAGE': {
            'property': SimfileDirectory.cdimage,
            'predefined': 'file-cd.png',
            'specified': '5.png',
        },
        'DISC': {
            'property': SimfileDirectory.disc,
            'predefined': 'file disc.png',
            'specified': '6.png',
        },
        'MUSIC': {
            'property': SimfileDirectory.music,
            'predefined': 'audio.ogg',
            'specified': '7.wav',
        },
    }

    def create_assets(self, dir):
        for _, asset_hash in TestSimfileDirectory.ASSET_PATHS.items():
            for asset_type in ('predefined', 'specified'):
                with open(os.path.join(dir, asset_hash[asset_type]), 'w'):
                    pass


    def test_predefined_assets(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        
        os.mkdir(dir)
        self.create_assets(dir)
        
        sm_file = SMSimfile.blank()
        sm_file.title = 'SM'
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        sd = SimfileDirectory('dir')

        self.assertEqual(sm_file, sd.simfile)

        for asset_name, asset_map in TestSimfileDirectory.ASSET_PATHS.items():
            expected = os.path.join(dir, asset_map['predefined'])
            accessor = asset_map['property'].fget(sd)
            self.assertEqual(expected, accessor, f'wrong path for {asset_name}')
    
    def test_specified_assets(self):
        dir = 'dir'
        sm_path = os.path.join(dir, 'sm_file.sm')
        
        os.mkdir(dir)
        self.create_assets(dir)
        
        sm_file = SMSimfile.blank()
        sm_file.title = 'SM'
        for asset_name, asset_hash in TestSimfileDirectory.ASSET_PATHS.items():
            sm_file[asset_name] = asset_hash['specified']
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        sd = SimfileDirectory('dir')

        self.assertEqual(sm_file, sd.simfile)

        for asset_name, asset_map in TestSimfileDirectory.ASSET_PATHS.items():
            expected = os.path.join(dir, asset_map['specified'])
            accessor = asset_map['property'].fget(sd)
            self.assertEqual(expected, accessor, f'wrong path for {asset_name}')
