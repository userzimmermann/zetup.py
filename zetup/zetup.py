# zetup.py
#
# Zimmermann's Python package setup.
#
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
from textwrap import dedent
from itertools import chain
from collections import OrderedDict
from subprocess import call

if sys.version_info[0] == 3:
    from configparser import ConfigParser
    # Just for simpler PY2/3 compatible code:
    unicode = str
else:
    from ConfigParser import ConfigParser

try:
    from setuptools import setup, Command, find_packages
except ImportError: # fallback
    # (setuptools should at least be available after package installation)
    from distutils.core import setup, Command

from .version import Version
from .requires import Requirements
from .extras import Extras
from .dist import Distribution
from .notebook import Notebook


class Zetup(object):
    def __init__(self, ZETUP_DIR='.'):
        # if not ZETUP_DIR:
        #     # Try to get the directory of this script,
        #     #  to correctly access VERSION, requirements.txt, ...
        #     try:
        #         __file__
        #     except: # Happens if exec()'d from SConstruct
        #         ZETUP_DIR = '.'
        #     else:
        #         ZETUP_DIR = os.path.realpath(os.path.dirname(__file__))
        self.ZETUP_DIR = ZETUP_DIR


        # Read the zetup config...
        config = ConfigParser()
        for fname in ['zetup.ini', 'zetup.cfg', 'zetuprc']:
            self.ZETUP_FILE = os.path.join(self.ZETUP_DIR, fname)
            if config.read(self.ZETUP_FILE):
                ##TODO: No print if run from installed package (under pkg/zetup/):
                ## print("zetup: Using config from %s" % fname)

                # The config file will be installed as pkg.zetup package_data:
                self.ZETUP_DATA = [fname]
                break
        else:
            raise RuntimeError("No zetup config found.")


        #... and store all setup options in UPPERCASE vars...
        self.NAME = config.sections()[0]

        config = dict(config.items(self.NAME))

        self.TITLE = config.get('title', self.NAME)
        self.DESCRIPTION = config['description'].strip().replace('\n', ' ')

        self.AUTHOR = re.match(r'^([^<]+)<([^>]+)>$', config['author'])
        self.AUTHOR, self.EMAIL = map(str.strip, self.AUTHOR.groups())
        self.URL = config['url']

        self.LICENSE = config['license']

        self.PYTHON = config['python'].split()

        self.PACKAGES = config.get('packages', [])
        if self.PACKAGES:
            # First should be the root package
            self.PACKAGES = self.PACKAGES.split()
        elif os.path.isdir(self.NAME):
            # Just assume distribution name == root package name
            self.PACKAGES = [self.NAME]

        self.CLASSIFIERS = config['classifiers'].strip() \
          .replace('\n::', ' ::').split('\n')
        self.CLASSIFIERS.append('Programming Language :: Python')
        for pyversion in self.PYTHON:
            self.CLASSIFIERS.append('Programming Language :: Python :: ' + pyversion)

        self.KEYWORDS = config['keywords'].split()
        if any(pyversion.startswith('3') for pyversion in self.PYTHON):
            self.KEYWORDS.append('python3')

        del config


        # The default pkg.zetup package for installing this script and ZETUP_DATA:
        if self.PACKAGES:
            self.ZETUP_PACKAGE = self.PACKAGES[0] + '.zetup'


        # Extend PACKAGES with all their subpackages:
        try:
            find_packages
        except NameError: #==> No setuptools
            pass
        else:
            self.PACKAGES.extend(chain(*(
              ['%s.%s' % (pkg, sub) for sub in find_packages(pkg)]
              for pkg in self.PACKAGES)))


        # Parse VERSION and requirements files
        #  and add them to pkg.zetup package_data...
        self.ZETUP_DATA += ['VERSION', 'requirements.txt']

        self.VERSION_FILE = os.path.join(self.ZETUP_DIR, 'VERSION')
        if os.path.exists(self.VERSION_FILE):
            self.VERSION = Version(open(self.VERSION_FILE).read().strip())
        else:
            self.VERSION_FILE = None
            try:
                import hgdistver
            except ImportError:
                self.VERSION = '0.0.0'
            else:
                self.VERSION = hgdistver.get_version()

        self.DISTRIBUTION = Distribution(
          self.NAME, self.PACKAGES and self.PACKAGES[0] or self.NAME, self.VERSION)

        self.REQUIRES = Requirements(
          open(os.path.join(self.ZETUP_DIR, 'requirements.txt')).read())

        # Look for optional extra requirements to use with setup's extras_require=
        self.EXTRAS = Extras()
        _re = re.compile(r'^requirements\.(?P<name>[^\.]+)\.txt$')
        for fname in sorted(os.listdir(self.ZETUP_DIR)):
            match = _re.match(fname)
            if match:
                self.ZETUP_DATA.append(fname)

                self.EXTRAS[match.group('name')] \
                  = open(os.path.join(self.ZETUP_DIR, fname)).read()


        # Are there IPython notebooks?
        self.NOTEBOOKS = OrderedDict()
        for fname in sorted(os.listdir(self.ZETUP_DIR)):
            name, ext = os.path.splitext(fname)
            if ext == '.ipynb':
                if name == 'README':
                    self.ZETUP_DATA.append(fname)
                self.NOTEBOOKS[name] = Notebook(os.path.join(self.ZETUP_DIR, 'README.ipynb'))


    def __call__(self, **setup_options):
        """Run setup() with options from zetup config
           and custom override `setup_options`.

        - Also adds additional setup commands:
          - ``conda``:
            conda package builder (with build config generator)
        """
        defaults = {
          'name': self.NAME,
          'version': str(self.VERSION),
          'description': self.DESCRIPTION,
          'author': self.AUTHOR,
          'author_email': self.EMAIL,
          'url': self.URL,
          'license': self.LICENSE,
          'install_requires': str(self.REQUIRES),
          'extras_require':
            {name: str(reqs) for name, reqs in self.EXTRAS.items()},
          'classifiers': self.CLASSIFIERS,
          'keywords': self.KEYWORDS,
          # 'cmdclass': SETUP_COMMANDS, # defined below
          }
        if self.PACKAGES:
            defaults.update({
              'package_dir': {self.ZETUP_PACKAGE: '.'},
              'packages': self.PACKAGES + [self.ZETUP_PACKAGE],
              'package_data': {self.ZETUP_PACKAGE: self.ZETUP_DATA},
              })
        for option, value in defaults.items():
            setup_options.setdefault(option, value)
        return setup(**setup_options)


    COMMANDS = []

    @classmethod
    def command(cls, func):
        name = func.__name__
        setattr(cls, name, func)
        cls.COMMANDS.append(name)


# If installed with pip, add all build directories and src/ subdirs
#  of implicitly downloaded requirements
#  to sys.path and os.environ['PYTHONPATH']
#  to make them importable during installation:
sysbuildpath = os.path.join(sys.prefix, 'build')
try:
    fnames = os.listdir(sysbuildpath)
except OSError:
    pass
else:
    if 'pip-delete-this-directory.txt' in fnames:
        pkgpaths = []
        for fn in fnames:
            path = os.path.join(sysbuildpath, fn)
            if not os.path.isdir(path):
                continue
            path = os.path.abspath(path)
            pkgpaths.append(path)

            srcpath = os.path.join(path, 'src')
            if os.path.isdir(srcpath):
                pkgpaths.append(srcpath)

        for path in pkgpaths:
            sys.path.insert(0, path)

        PYTHONPATH = os.environ.get('PYTHONPATH')
        PATH = ':'.join(pkgpaths)
        if PYTHONPATH is None:
            os.environ['PYTHONPATH'] = PATH
        else:
            os.environ['PYTHONPATH'] = ':'.join([PATH, PYTHONPATH])


# If this is a locally imported zetup.py in zetup's own repo...
# if (NAME == 'zetup' #==> is in zetup's own package/repo
#     and os.path.basename(__file__).startswith('zetup')
#     #"=> was not exec()'d from setup.py
#     and not 'zetup.zetup' in sys.modules
#     #"=> was not imported as subpackage
#     ):
#     #... then fake the interface of the installed zetup package...
#     import zetup # import itself as faked subpackage

#     ## __path__ = [os.path.join(ZETUP_DIR, 'zetup')]
#     __path__ = [ZETUP_DIR]
#     # Exec the __init__ which gets installed in top level zetup package:
#     exec(open('__init__.py').read().replace('from . import zetup', ''))
