#!/usr/bin/env python
"""Setup file and install script SciLife python scripts.
"""
from setuptools import setup, find_packages
import sys
import os
import glob

setup(name = "DB2LIMS",
	version = "1.0",
      	author = "Maya Brandi",
      	author_email = "maya.brandi@scilifelab.se",
      	description = "Pacage make and load statusDB objects out of Lims data",
	py_modules = ['objectsDB','project_summary_upload','statusDB_utils']
      )

