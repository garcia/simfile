from setuptools import setup, find_packages

from simfile import __version__ as version


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='simfile',
    version=version,
    description='Modern simfile library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ash Garcia',
    author_email='python-simfile@garcia.sh',
    url='https://github.com/garcia/simfile',
    packages=find_packages(exclude=['*.tests']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ],
    license='MIT',
    keywords='stepmania simfile sm ssc',
    zip_safe=False,
    install_requires=[
        'msdparser>=1.0.0-alpha.2',
    ],
    python_requires='>=3.6',
    tests_require=[
        'pyfakefs'
    ],
    command_options={
        'build_sphinx': {
            'version': ('setup.py', version),
        },
    },
)