from __future__ import print_function

import sys
import os

## from setuptools import Distribution
from pkg_resources import working_set ## get_distribution


egg_info = 'zetup.egg-info'
if os.path.exists(egg_info):
    print("zetup: Removing possibly outdated %s/" % egg_info)
    for fname in os.listdir(egg_info):
        os.remove(os.path.join(egg_info, fname))
    os.rmdir(egg_info)
    del working_set.by_key['zetup']


sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
from zetup import Zetup, DistributionNotFound, VersionConflict
try:
    import zetup.commands
except (ImportError, DistributionNotFound, VersionConflict):
    #==> no zetup commands available
    # standard setup commands work anyway
    pass


## setup_req = 'setuptools >= 15.0'
## try:
##     get_distribution(setup_req)
## except VersionConflict:
##     for mod in ['setuptools', 'pkg_resources']:
##         for name, _ in list(sys.modules.items()):
##             if name == mod or name.startswith(mod + '.'):
##                 del sys.modules[name]
##     sys.path.insert(0, Distribution().fetch_build_egg(setup_req))


zfg = Zetup()

setup = zfg.setup
setup['package_data']['zetup.commands.make'] = [
  'templates/*.jinja',
  'templates/package/*.jinja',
  ]
setup(
  ## setup_requires=setup_req,
  ## setup_requires=['hgdistver >= 0.25'],

  ## get_version_from_scm=True,

  entry_points={
    'distutils.setup_keywords': [
      'use_zetup = zetup:setup_entry_point',
      ],
    'console_scripts': [
      'zetup = zetup.script:run',
      ]},
  )
