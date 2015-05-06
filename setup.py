"""
Setup.py for FFs
"""
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

HERE = os.path.realpath(os.path.dirname(__file__))

VERSION_FILE = os.path.join(HERE, "ffs/_version.py")
verstrline = open(VERSION_FILE, "rt").read()
VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
mo = re.search(VSRE,  verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {0}".format(VERSION_FILE))

os.chdir(HERE)

install_requires = ['six>=1.2.0']
if sys.version_info < (2, 6):
    install_requires.append('smplejson')

setup(
    name = "ffs",
    version = VERSION,
    author = "David Miller",
    author_email = "david@deadpansincerity.com",
    url = "http://www.deadpansincerity.com/docs/ffs",
    description = "Python Filesystem Api helpers",
    long_description = open(os.path.join(HERE, 'README.rst')).read() + "\n\n" +  open(os.path.join(HERE, 'HISTORY.rst')).read(),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3.1",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    install_requires=install_requires,
    packages = ['ffs', 'ffs.contrib'],
    )
