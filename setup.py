#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='simfile',
      version='2.0.0-alpha',
      author='Ash Garcia',
      author_email='python-simfile@garcia.sh'
      description='A simfile parser for Python',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/garcia/simfile',
      packages=['simfile'],
)