import os
from setuptools import setup, find_packages


def get_version():
    initpath = os.path.join(os.path.dirname(__file__), "simfile/__init__.py")
    with open(initpath) as initfile:
        for line in initfile:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


version = get_version()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simfile",
    version=version,
    description="Modern simfile library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ash Garcia",
    author_email="python-simfile@garcia.sh",
    url="https://github.com/garcia/simfile",
    packages=find_packages(exclude=["*.tests"]),
    package_data={
        "simfile": ["py.typed"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    license="MIT",
    keywords="stepmania simfile sm ssc",
    zip_safe=False,
    install_requires=[
        "msdparser~=2.0.0",
        "fs~=2.4.15",
    ],
    python_requires=">=3.6",
    tests_require=["pyfakefs"],
    command_options={
        "build_sphinx": {
            "version": ("setup.py", version),
        },
    },
)
