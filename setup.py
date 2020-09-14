#!/usr/bin/env python3
from setuptools import setup

from simfile import __version__ as version


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='simfile',
    version=version,
    author='Ash Garcia',
    author_email='python-simfile@garcia.sh',
    description='Modern simfile library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/garcia/simfile',
    packages=['simfile'],
    command_options={
        'build_sphinx': {
            'version': ('setup.py', version),
        },
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ],
    install_requires=[
        'msdparser>=0.1.3',
    ],
    tests_require=[
        'pyfakefs'
    ],
    zip_safe=False,
)