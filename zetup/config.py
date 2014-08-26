# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
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

import sys
import os
import re
from itertools import chain
from collections import OrderedDict
if sys.version_info[0] == 3:
    from configparser import ConfigParser
    # Just for simpler PY2/3 compatible code:
    unicode = str
else:
    from ConfigParser import ConfigParser

from setuptools import find_packages

from .version import Version
from .requires import Requirements
from .extras import Extras
from .dist import Distribution
from .notebook import Notebook


def load_zetup_config(path, cfg):
    """Load zetup config from directory in `path`
       and store keywords as attributes to `cfg` object.
    """
    cfg.ZETUP_DIR = path

    # Read the zetup config...
    config = ConfigParser()
    for fname in ['zetup.ini', 'zetup.cfg', 'zetuprc']:
        cfg.ZETUP_FILE = os.path.join(cfg.ZETUP_DIR, fname)
        if config.read(cfg.ZETUP_FILE):
            ##TODO: No print if run from installed package (under pkg/zetup/):
            ## print("zetup: Using config from %s" % fname)

            # The config file will be installed as pkg.zetup package_data:
            cfg.ZETUP_DATA = [fname]
            break
    else:
        raise RuntimeError("No zetup config found.")

    #... and store all setup options in UPPERCASE vars...
    cfg.NAME = config.sections()[0]

    config = dict(config.items(cfg.NAME))

    cfg.TITLE = config.get('title', cfg.NAME)
    cfg.DESCRIPTION = config['description'].strip().replace('\n', ' ')

    cfg.AUTHOR = re.match(r'^([^<]+)<([^>]+)>$', config['author'])
    cfg.AUTHOR, cfg.EMAIL = map(str.strip, cfg.AUTHOR.groups())
    cfg.URL = config['url']

    cfg.LICENSE = config['license']

    cfg.PYTHON = config['python'].split()

    cfg.PACKAGES = config.get('packages', [])
    if cfg.PACKAGES:
        # First should be the root package
        cfg.PACKAGES = cfg.PACKAGES.split()
    elif os.path.isdir(os.path.join(cfg.ZETUP_DIR, cfg.NAME)):
        # Just assume distribution name == root package name
        cfg.PACKAGES = [cfg.NAME]

    cfg.ZETUP_CONFIG_PACKAGE = config.get(
      'zetup_config_package', False)
    if cfg.ZETUP_CONFIG_PACKAGE:
        cfg.ZETUP_CONFIG_PACKAGE = cfg.ZETUP_CONFIG_PACKAGE.strip()
    if cfg.ZETUP_CONFIG_PACKAGE == '':
        cfg.ZETUP_CONFIG_PACKAGE = cfg.PACKAGES[0] + '.zetup_config'

    cfg.CLASSIFIERS = config['classifiers'].strip() \
      .replace('\n::', ' ::').split('\n')
    cfg.CLASSIFIERS.append('Programming Language :: Python')
    for pyversion in cfg.PYTHON:
        cfg.CLASSIFIERS.append('Programming Language :: Python :: ' + pyversion)

    cfg.KEYWORDS = config['keywords'].split()
    if any(pyversion.startswith('3') for pyversion in cfg.PYTHON):
        cfg.KEYWORDS.append('python3')

    # The default pkg.zetup package for installing this script and ZETUP_DATA:
    if cfg.PACKAGES:
        cfg.ZETUP_PACKAGE = cfg.PACKAGES[0] + '.zetup'

    # Extend PACKAGES with all their subpackages:
    try:
        find_packages
    except NameError: #==> No setuptools
        pass
    else:
        cfg.PACKAGES.extend(chain(*(
          ['%s.%s' % (pkg, sub) for sub in find_packages(pkg)]
          for pkg in cfg.PACKAGES)))

    if cfg.ZETUP_CONFIG_PACKAGE:
        cfg.PACKAGES.append(cfg.ZETUP_CONFIG_PACKAGE)

    # Parse VERSION and requirements files
    #  and add them to pkg.zetup package_data...
    cfg.ZETUP_DATA += ['VERSION', 'requirements.txt']

    cfg.VERSION_FILE = os.path.join(cfg.ZETUP_DIR, 'VERSION')
    if os.path.exists(cfg.VERSION_FILE):
        cfg.VERSION = open(cfg.VERSION_FILE).read().strip()
    else:
        cfg.VERSION_FILE = None
        try:
            import hgdistver
        except ImportError:
            cfg.VERSION = None
        else:
            cfg.VERSION = hgdistver.get_version()
    if cfg.VERSION:
        cfg.VERSION = Version(cfg.VERSION)

    cfg.DISTRIBUTION = Distribution(
      cfg.NAME, cfg.PACKAGES and cfg.PACKAGES[0] or cfg.NAME, cfg.VERSION)

    cfg.REQUIRES = Requirements(
      open(os.path.join(cfg.ZETUP_DIR, 'requirements.txt')).read())

    # Look for optional extra requirements to use with setup's extras_require=
    cfg.EXTRAS = Extras()
    _re = re.compile(r'^requirements\.(?P<name>[^\.]+)\.txt$')
    for fname in sorted(os.listdir(cfg.ZETUP_DIR)):
        match = _re.match(fname)
        if match:
            cfg.ZETUP_DATA.append(fname)

            cfg.EXTRAS[match.group('name')] \
              = open(os.path.join(cfg.ZETUP_DIR, fname)).read()

    # Are there IPython notebooks?
    cfg.NOTEBOOKS = OrderedDict()
    for fname in sorted(os.listdir(cfg.ZETUP_DIR)):
        name, ext = os.path.splitext(fname)
        if ext == '.ipynb':
            if name == 'README':
                cfg.ZETUP_DATA.append(fname)
            cfg.NOTEBOOKS[name] = Notebook(
              os.path.join(cfg.ZETUP_DIR, fname))
