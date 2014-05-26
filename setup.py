# -*- coding: UTF-8 -*-

from os.path import dirname
import sys

import setuptools
from distutils.core import setup

# http://stackoverflow.com/a/7071358/735926
import re
VERSIONFILE='rogue_scores/__init__.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(
    name='rogue_scores',
    version=verstr,
    author='Baptiste Fontaine',
    author_email='b@ptistefontaine.fr',
    packages=['rogue_scores'],
    url='https://github.com/bfontaine/rogue_scores',
    license=open('LICENSE', 'r').read(),
    description='online Rogue scores leaderboard',
    long_description="""\
rogue_scores bundles a Web server for an online Rogue scores leaderboard as \
well as a Python script to upload local scores to the server""",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'requests >= 2.3.0',
    ],
    entry_points={
        'console_scripts':[
            'rogue_scores = rogue_scores.cli:run'
        ]
    },
)
