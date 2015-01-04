# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

__all__ = ['load_zetup_config']

import sys
import os
import re
from textwrap import dedent
from itertools import chain
from collections import OrderedDict
from warnings import warn
if sys.version_info[0] == 3:
    from configparser import ConfigParser
    # Just for simpler PY2/3 compatible code:
    unicode = str
else:
    from ConfigParser import ConfigParser

from .version import Version
from .requires import Requirements
from .extras import Extras
from .dist import Distribution
from .notebook import Notebook


TRUE = True, 'true', 'yes'
FALSE = False, 'false', 'no'


def load_zetup_config(path, zfg):
    """Load zetup config from directory in `path`
       and store keywords as attributes to `zfg` object.
    """
    zfg.ZETUP_DIR = path

    # Read the zetup config...
    config = ConfigParser()
    for fname in ['zetup.ini', 'zetup.cfg', 'zetuprc']:
        zfg.ZETUP_FILE = os.path.join(zfg.ZETUP_DIR, fname)
        if config.read(zfg.ZETUP_FILE):
            ##TODO: No print if run from installed package (under pkg/zetup/):
            ## print("zetup: Using config from %s" % fname)

            # The config file will be installed as pkg.zetup package_data:
            zfg.ZETUP_DATA = [fname]
            break
    else:
        raise RuntimeError("No zetup config found.")

    #... and store all setup options in UPPERCASE vars...
    zfg.NAME = config.sections()[0]

    # get a section dictionary with normalized option names as keys
    config = {re.sub(r'[^a-z0-9]', '', option.lower()): value
              for option, value in config.items(zfg.NAME)}

    zfg.TITLE = config.get('title', zfg.NAME)
    zfg.DESCRIPTION = config['description'].strip().replace('\n', ' ')

    zfg.AUTHOR = re.match(r'^([^<]+)<([^>]+)>$', config['author'])
    zfg.AUTHOR, zfg.EMAIL = map(str.strip, zfg.AUTHOR.groups())
    zfg.URL = config['url']

    zfg.LICENSE = config['license']

    zfg.PYTHON = config['python'].split()

    zfg.PACKAGES = config.get('packages', [])
    if zfg.PACKAGES:
        # First should be the root package
        zfg.PACKAGES = zfg.PACKAGES.split()
    elif os.path.isdir(os.path.join(zfg.ZETUP_DIR, zfg.NAME)):
        # Just assume distribution name == root package name
        zfg.PACKAGES = [zfg.NAME]

    zfg.ZETUP_CONFIG_PACKAGE = config.get(
      'zetupconfigpackage', False)
    if zfg.ZETUP_CONFIG_PACKAGE:
        if zfg.ZETUP_CONFIG_PACKAGE in TRUE:
            zfg.ZETUP_CONFIG_PACKAGE = zfg.PACKAGES[0] + '.zetup_config'
        elif zfg.ZETUP_CONFIG_PACKAGE not in FALSE:
            zfg.ZETUP_CONFIG_PACKAGE = zfg.ZETUP_CONFIG_PACKAGE.strip()

    zfg.ZETUP_CONFIG_MODULE = config.get(
      'zetupconfigmodule', False)
    if zfg.ZETUP_CONFIG_MODULE:
        if zfg.ZETUP_CONFIG_MODULE in TRUE:
            zfg.ZETUP_CONFIG_MODULE = zfg.PACKAGES[0] + '.zetup_config'
        elif zfg.ZETUP_CONFIG_MODULE not in FALSE:
            zfg.ZETUP_CONFIG_MODULE = zfg.ZETUP_CONFIG_MODULE.strip()

    zfg.CLASSIFIERS = config['classifiers'].strip() \
      .replace('\n::', ' ::').split('\n')
    zfg.CLASSIFIERS.append('Programming Language :: Python')
    for pyversion in zfg.PYTHON:
        zfg.CLASSIFIERS.append(
          'Programming Language :: Python :: ' + pyversion)

    zfg.KEYWORDS = config['keywords'].split()
    if any(pyversion.startswith('3') for pyversion in zfg.PYTHON):
        zfg.KEYWORDS.append('python3')

    # The default pkg.zetup package for installing this script and ZETUP_DATA:
    if zfg.PACKAGES:
        zfg.ZETUP_PACKAGE = zfg.PACKAGES[0] + '.zetup'

    # Extend PACKAGES with all their subpackages:
    try:
        # need to import dynamically for packages dealing with namespaces
        #  because setuptools try to import namespace packages
        #  before setuptools.find_packages gets available
        from setuptools import find_packages
    except ImportError: #==> No setuptools
        pass
    else:
        zfg.PACKAGES.extend(chain(*(
          ['%s.%s' % (pkg, sub) for sub in find_packages(pkg)]
          for pkg in zfg.PACKAGES if os.path.isdir(pkg))))

    if zfg.ZETUP_CONFIG_PACKAGE:
        zfg.PACKAGES.append(zfg.ZETUP_CONFIG_PACKAGE)

    # Parse VERSION and requirements files
    #  and add them to pkg.zetup package_data...
    zfg.ZETUP_DATA += ['VERSION', 'requirements.txt']

    zfg.VERSION_FILE = os.path.join(zfg.ZETUP_DIR, 'VERSION')
    if os.path.exists(zfg.VERSION_FILE):
        zfg.VERSION = open(zfg.VERSION_FILE).read().strip()
    else:
        zfg.VERSION_FILE = None
        try:
            import hgdistver
        except ImportError:
            warn(dedent("""
              No hgdistver found.
              Zetup needs hgdistver to get package version from repository.
              """))
            zfg.VERSION = None
        else:
            version = hgdistver.get_version()
            # the hyphen-revision-hash part after .dev# version strings
            # results in wrong version comparisons
            # via pkg_resources.parse_version()
            zfg.VERSION = version.split('-')[0]
    if zfg.VERSION:
        zfg.VERSION = Version(zfg.VERSION)

    zfg.DISTRIBUTION = Distribution(
      zfg.NAME, zfg.PACKAGES and zfg.PACKAGES[0] or zfg.NAME, zfg.VERSION)

    zfg.REQUIRES = Requirements(
      open(os.path.join(zfg.ZETUP_DIR, 'requirements.txt')).read())

    # Look for optional extra requirements to use with setup's extras_require=
    zfg.EXTRAS = Extras()
    _re = re.compile(r'^requirements\.(?P<name>[^\.]+)\.txt$')
    for fname in sorted(os.listdir(zfg.ZETUP_DIR)):
        match = _re.match(fname)
        if match:
            zfg.ZETUP_DATA.append(fname)

            zfg.EXTRAS[match.group('name')] \
              = open(os.path.join(zfg.ZETUP_DIR, fname)).read()

    # Are there IPython notebooks?
    zfg.NOTEBOOKS = OrderedDict()
    for fname in sorted(os.listdir(zfg.ZETUP_DIR)):
        name, ext = os.path.splitext(fname)
        if ext == '.ipynb':
            if name == 'README':
                zfg.ZETUP_DATA.append(fname)
            zfg.NOTEBOOKS[name] = Notebook(
              os.path.join(zfg.ZETUP_DIR, fname))
