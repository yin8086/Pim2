from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

options = {'py2exe': {'bundle_files': 1, 'compressed': True}} 
setup(options = options, zipfile = None,console=["Pim2Export.py"])
setup(options = options, zipfile = None,console=["Pim2Import.py"])