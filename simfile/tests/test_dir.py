import os

from fs.zipfs import ZipFS
from pyfakefs.fake_filesystem_unittest import TestCase # type: ignore

from simfile.dir import SimfileDirectory, SimfilePack
from simfile.sm import SMSimfile
from simfile.ssc import SSCSimfile


class TestSimfileDirectory(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory('testdata')

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
    
    def test_with_filesystem(self):
        zip_fs = ZipFS('testdata/testdata.zip')

        sd = SimfileDirectory('Springtime', filesystem=zip_fs)
        
        self.assertIsNone(sd.sm_path)
        self.assertEqual('Springtime/Springtime.ssc', sd.ssc_path)
        
        sim = sd.open()
        self.assertEqual('Springtime', sim.title)


class TestSimfilePack(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory('testdata')
    
    def make_pack(self, pack_dir):
        os.mkdir(pack_dir)
        
        a_dir = os.path.join(pack_dir, 'Simfile A')
        os.mkdir(a_dir)
        a_sm_path = os.path.join(a_dir, 'a.sm')

        b_dir = os.path.join(pack_dir, 'Simfile B')
        os.mkdir(b_dir)
        b_sm_path = os.path.join(b_dir, 'b.sm')
        b_ssc_path = os.path.join(b_dir, 'b.ssc')

        no_simfile_dir = os.path.join(pack_dir, 'tmp')
        os.mkdir(no_simfile_dir)
        no_simfile_file = os.path.join(no_simfile_dir, 'tmp.txt')

        for blank_file in (a_sm_path, b_sm_path, b_ssc_path, no_simfile_file):
            with open(blank_file, 'w') as writer:
                if blank_file.endswith('.sm'):
                    SMSimfile.blank().serialize(writer)
                if blank_file.endswith('.ssc'):
                    SSCSimfile.blank().serialize(writer)
        
        # TODO: find a better way to manage this
        return a_dir, a_sm_path, b_dir, b_sm_path, b_ssc_path
    
    def test_simfile_discovery(self):
        pack_dir = 'My Pack'
        a_dir, a_sm_path, b_dir, b_sm_path, b_ssc_path = self.make_pack(
            pack_dir,
        )

        sp = SimfilePack(pack_dir)
        self.assertEqual(set(sp.simfile_dir_paths), set((a_dir, b_dir)))
        
        a_index = sp.simfile_dir_paths.index(a_dir)
        b_index = sp.simfile_dir_paths.index(b_dir)
        
        simfile_dirs = list(sp.simfile_dirs())
        self.assertEqual(2, len(simfile_dirs))
        simfile_dir_a = simfile_dirs[a_index]
        simfile_dir_b = simfile_dirs[b_index]
        self.assertEqual(a_sm_path, simfile_dir_a.sm_path)
        self.assertIsNone(simfile_dir_a.ssc_path)
        self.assertEqual(b_sm_path, simfile_dir_b.sm_path)
        self.assertEqual(b_ssc_path, simfile_dir_b.ssc_path)

        simfiles = list(sp.simfiles())
        self.assertEqual(2, len(simfiles))
        simfile_a = simfiles[a_index]
        simfile_b = simfiles[b_index]
        self.assertIsInstance(simfile_a, SMSimfile)
        self.assertIsInstance(simfile_b, SSCSimfile)
    
    def test_simfile_discovery_with_trailing_slash(self):
        pack_dir = 'My Pack'
        a_dir, a_sm_path, b_dir, b_sm_path, b_ssc_path = self.make_pack(
            pack_dir,
        )

        sp = SimfilePack(pack_dir + os.path.sep)
        self.assertEqual(set(sp.simfile_dir_paths), set((a_dir, b_dir)))
        
        a_index = sp.simfile_dir_paths.index(a_dir)
        b_index = sp.simfile_dir_paths.index(b_dir)
        
        simfile_dirs = list(sp.simfile_dirs())
        self.assertEqual(2, len(simfile_dirs))
        simfile_dir_a = simfile_dirs[a_index]
        simfile_dir_b = simfile_dirs[b_index]
        self.assertEqual(a_sm_path, simfile_dir_a.sm_path)
        self.assertIsNone(simfile_dir_a.ssc_path)
        self.assertEqual(b_sm_path, simfile_dir_b.sm_path)
        self.assertEqual(b_ssc_path, simfile_dir_b.ssc_path)

        simfiles = list(sp.simfiles())
        self.assertEqual(2, len(simfiles))
        simfile_a = simfiles[a_index]
        simfile_b = simfiles[b_index]
        self.assertIsInstance(simfile_a, SMSimfile)
        self.assertIsInstance(simfile_b, SSCSimfile)
    
    def test_name(self):
        enclosing_dir = 'Songs'
        os.mkdir(enclosing_dir)

        pack_name = 'My Pack'
        pack_dir = os.path.join(enclosing_dir, pack_name)
        a_dir, a_sm_path, b_dir, b_sm_path, b_ssc_path = self.make_pack(
            pack_dir,
        )
        
        sp = SimfilePack(pack_dir)
        self.assertEqual(pack_name, sp.name)

    def test_name_with_trailing_slash(self):
        enclosing_dir = 'Songs'
        os.mkdir(enclosing_dir)

        pack_name = 'My Pack'
        pack_dir = os.path.join(enclosing_dir, pack_name)
        a_dir, a_sm_path, b_dir, b_sm_path, b_ssc_path = self.make_pack(
            pack_dir,
        )

        sp = SimfilePack(pack_dir + os.path.sep)
        self.assertEqual(pack_name, sp.name)
    
    def test_banner(self):
        enclosing_dir = 'Songs'
        os.mkdir(enclosing_dir)

        pack_name = 'My Pack'
        pack_dir = os.path.join(enclosing_dir, pack_name)
        a_dir, a_sm_path, b_dir, b_sm_path, b_ssc_path = self.make_pack(
            pack_dir,
        )

        # In descending order of priority
        # This list will be mutated as each banner is deleted from the test FS
        pack_banner_paths = [
            os.path.join(pack_dir, 'banner.png'),
            os.path.join(pack_dir, 'artwork.jpg'),
            os.path.join(pack_dir, 'cdtitle.bmp'),
            os.path.join(enclosing_dir, 'My Pack.jpg'),
            os.path.join(enclosing_dir, 'My Pack.jpeg'),
        ]

        other_paths = [
            os.path.join(enclosing_dir, 'Other Pack.png'),
            os.path.join(enclosing_dir, 'My Pack.webp'),
            os.path.join(pack_dir, 'idk.webp'),
            os.path.join(a_dir, 'a.png'),
        ]

        for image_location in pack_banner_paths + other_paths:
            with open(image_location, 'w') as _:
                pass
        
        # Check against the highest priority pack banner, then delete it to
        # check the next highest priority until no banners remain
        iteration = 1
        while pack_banner_paths:
            pack_banner_path = pack_banner_paths.pop(0)
            sp = SimfilePack(pack_dir)
            
            self.assertEqual(pack_banner_path, sp.banner(), f"Wrong banner path on iteration={iteration}")

            os.remove(pack_banner_path)
            iteration += 1
        
        # No banners left - we shouldn't return any of the other image paths
        sp = SimfilePack(pack_dir)
        self.assertIsNone(sp.banner())
    
    def test_with_filesystem(self):
        zip_fs = ZipFS('testdata/testdata.zip')

        sp = SimfilePack('/', filesystem=zip_fs)

        self.assertEqual(
            set(('/L9', '/nekonabe', '/Springtime')),
            set(sp.simfile_dir_paths)
        )

        simfile_dirs = list(sp.simfile_dirs())
        simfile_paths = set((sd.sm_path, sd.ssc_path) for sd in simfile_dirs)
        self.assertEqual(
            set((
                ('/nekonabe/nekonabe.sm', None),
                (None, '/L9/L9.ssc'),
                (None, '/Springtime/Springtime.ssc'),
            )),
            simfile_paths,
        )

        simfiles = list(sp.simfiles())
        self.assertEqual(
            set(('L9', '猫鍋', 'Springtime')),
            set(sim.title for sim in simfiles),
        )