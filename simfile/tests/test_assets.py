import os

from pyfakefs.fake_filesystem_unittest import TestCase # type: ignore

from ..sm import SMSimfile
from ..assets import Assets


ASSET_PATHS = {
    'BANNER': {
        'property': Assets.banner,
        'predefined': 'banner.png',
        'specified': '1.png',
    },
    'BACKGROUND': {
        'property': Assets.background,
        'predefined': 'background.png',
        'specified': '2.png',
    },
    'CDTITLE': {
        'property': Assets.cdtitle,
        'predefined': 'cdtitle.png',
        'specified': '3.png',
    },
    'JACKET': {
        'property': Assets.jacket,
        'predefined': 'jacket.png',
        'specified': '4.png',
    },
    'CDIMAGE': {
        'property': Assets.cdimage,
        'predefined': 'file-cd.png',
        'specified': '5.png',
    },
    'DISC': {
        'property': Assets.disc,
        'predefined': 'file disc.png',
        'specified': '6.png',
    },
    'MUSIC': {
        'property': Assets.music,
        'predefined': 'audio.ogg',
        'specified': '7.wav',
    },
}


class TestAssets(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def create_assets(self, dir):
        for _, asset_hash in ASSET_PATHS.items():
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
        
        sd = Assets('dir')

        self.assertEqual(sm_file, sd.simfile)

        for asset_name, asset_map in ASSET_PATHS.items():
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
        for asset_name, asset_hash in ASSET_PATHS.items():
            sm_file[asset_name] = asset_hash['specified']
        with open(sm_path, 'w') as writer:
            sm_file.serialize(writer)
        
        sd = Assets('dir')

        self.assertEqual(sm_file, sd.simfile)

        for asset_name, asset_map in ASSET_PATHS.items():
            expected = os.path.join(dir, asset_map['specified'])
            accessor = asset_map['property'].fget(sd)
            self.assertEqual(expected, accessor, f'wrong path for {asset_name}')
