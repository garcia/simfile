#!/usr/bin/env python
from distutils.core import setup
import os
import sys

from simfile import __version__

setup(name='simfile',
      version=__version__,
      description='A simfile library for Python',
      author='Grant Garcia',
      py_modules=['simfile'],
)