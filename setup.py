#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages


py_version = sys.version_info[:2]
if py_version < (3, 8):
    print(f"arkiver requires Python 3.8+ ({py_version} detected).")
    sys.exit(-1)


version = open("__version__.py", "r").read().strip()
setup(
    name="arkiver",
    version=version,
    description="Store websites locally, in a variety of formats",
    url="http://github.com/jensecj/arkiver",
    author="Jens Christian Jensen",
    author_email="jensecj@gmail.com",
    packages=find_packages(),
    entry_points={"console_scripts": ["arkiver = arkiver.cli:main"]},
    zip_safe=False,
)
