#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages


py_version = sys.version_info[:2]
if py_version < (3, 8):
    print(f"arkiv requires Python 3.8+ ({py_version} detected).")
    sys.exit(-1)


version = open("__version__.py", "r").read().strip()
setup(
    name="arkiv",
    version=version,
    description="Store websites locally, in a variety of formats",
    url="http://github.com/jensecj/arkiv",
    author="Jens C. Jensen",
    author_email="jensecj@gmail.com",
    packages=find_packages(),
    entry_points={"console_scripts": ["arkiv = arkiv.cli:main"]},
    zip_safe=False,
)
