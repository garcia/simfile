from distutils.core import setup
import py2exe

setup(console=['adjustoffset.py', 'clicktrack.py'],
      options={'py2exe': {'includes': ['hsaudiotag']}})