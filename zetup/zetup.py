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

__all__ = ['Zetup']

import sys
import os
from subprocess import call
try:
    from setuptools import setup, Command
except ImportError: # fallback
    # (setuptools should at least be available after package installation)
    from distutils.core import setup, Command

from .config import load_zetup_config


class Zetup(object):
    def __init__(self, ZETUP_DIR='.'):
        """Load and store zetup config from `ZETUP_DIR`
           as attributes in `self`.
        """
        load_zetup_config(ZETUP_DIR, zfg=self)

    @property
    def config(self):
        """Get the zetup config as dictionary.

        - Actually just return self.__dict__ because all attr assignments
          come from :func:`.config.load_zetup_config` in :meth:`.__init__`
          and are therefore just the config.
        """
        return self.__dict__

    def __getitem__(self, name):
        return self.config[name]

    @property
    def config_py(self):
        """Get the zetup config as Python code for writing to a .py module.
        """
        def items():
            for name, value in self.config.items():
                if name in [
                  'NOTEBOOKS',
                  ] or name.startswith('ZETUP') or name.endswith('FILE'):
                    continue
                try:
                    py = value.py
                except AttributeError:
                    py = repr(value)
                yield "%s = %s" % (name, py)

        return '\n\n'.join(items())

    def setup_keywords(self):
        """Get a dictionary of `setup()` keywords generated from zetup config.
        """
        keywords = {
          'name': self.NAME,
          'description': self.DESCRIPTION,
          'author': self.AUTHOR,
          'author_email': self.EMAIL,
          'url': self.URL,
          'license': self.LICENSE,
          'setup_requires': str(self.SETUP_REQUIRES or ''),
          'install_requires': str(self.REQUIRES or ''),
          'extras_require':
            {name: str(reqs) for name, reqs in self.EXTRAS.items()},
          # always provide empty default collections
          # to make sure that any custom setup hooks
          # can always directly add stuff
          # even if no data defined in zetup config
          'packages': [],
          'package_dir': {},
          'package_data': {},
          'py_modules': self.MODULES or [],
          'classifiers': self.CLASSIFIERS or [],
          'keywords': self.KEYWORDS or [],
          }
        if self.EXTRAS:
            keywords['extras_require']['all'] = self.EXTRAS['all']
        if self.VERSION:
            keywords['version'] = str(self.VERSION)
        if self.PACKAGES:
            namespaces = set()
            for pkg in self.PACKAGES:
                main = pkg.split('.')[0]
                if not os.path.exists(os.path.join(main, '__init__.py')):
                    namespaces.add(main)
            if namespaces:
                keywords['namespace_packages'] = list(namespaces)
            keywords['packages'] = self.PACKAGES
        if self.ZETUP_CONFIG_PACKAGE:
            keywords['package_dir'][self.ZETUP_CONFIG_PACKAGE] = '.'
            keywords['package_data'][self.ZETUP_CONFIG_PACKAGE] \
              = self.ZETUP_DATA
        cmdclasses = {}
        for cmdname in self.COMMANDS:
            cmdmethod = getattr(self, cmdname)

            class ZetupCommand(Command):
                # Must override options handling stuff from Command base...
                user_options = []

                def initialize_options(self):
                    pass

                def finalize_options(self):
                    pass

                run = staticmethod(cmdmethod)

            ZetupCommand.__name__ = cmdname
            cmdclasses[cmdname] = ZetupCommand

        keywords['cmdclass'] = cmdclasses
        return keywords

    @property
    def setup(self):
        return Setup(zetup=self)

    def __call__(self, subprocess=False, **setup_keywords):
        """Run `setup()` with generated keywords from zetup config
           and custom override `setup_keywords`.

        - If `subprocess` is True, run the dynamically generated setup.py
          (if zetup's extra 'commands' requirements are installed)
          with parameters from sys.argv in an external python process
          instead of directly calling setuptools.setup()
        """
        return self.setup(subprocess=subprocess, **setup_keywords)

    COMMANDS = []

    @classmethod
    def command(cls, args=None, depends=None):
        return CommandDeco(cls, args, depends)


class Setup(dict):
    def __init__(self, zetup):
        dict.__init__(self, zetup.setup_keywords())
        self.zetup = zetup

    def __call__(self, subprocess=False, **keywords):
        """Run `setup()` with generated keywords from zetup config
           and custom override `keywords`.

        - If `subprocess` is True, run python setup.py with sys.argv
          (see :meth:`Zetup.__call__` for details)
        """
        keywords = dict(self, **keywords)
        if 'make' in Zetup.COMMANDS:
            make_targets = ['VERSION', 'setup.py', 'zetup_config']
            if self.zetup.ZETUP_CONFIG_PACKAGE:
                make_targets.append('__init__.py')
            if self.zetup.ZETUP_CONFIG_MODULE:
                make_targets.append('package/zetup_config.py')
            with self.zetup.make(targets=make_targets, skip_existing=True):
                if subprocess:
                    return call([sys.executable, 'setup.py']
                                + sys.argv[1:])

                return setup(**keywords)
        return setup(**keywords)


class CommandDeco(object):
    def __init__(self, zetupcls, args=None, depends=None):
        self.zetupcls = zetupcls
        self.args = args
        self.make_targets = depends and list(depends)

    def __call__(self, func):
        """Add a command function as method to :class:`Zetup`
           and store its name in `cls.COMMANDS`.

        - Used in `zetup.commands.*` to sparate command implementations.
        """
        targets = self.make_targets

        def cmdmethod(self, args=None, **kwargs):
            if not targets:
                return func(self, args, **kwargs)
            with self.make(targets=targets, skip_existing=True):
                return func(self, args, **kwargs)

        name = cmdmethod.__name__ = func.__name__
        cmdmethod.args = self.args

        setattr(self.zetupcls, name, cmdmethod)
        self.zetupcls.COMMANDS.append(name)


# If installed with pip, add all build directories and src/ subdirs
#  of implicitly downloaded requirements
#  to sys.path and os.environ['PYTHONPATH']
#  to make them importable during installation:
# sysbuildpath = os.path.join(sys.prefix, 'build')
# try:
#     fnames = os.listdir(sysbuildpath)
# except OSError:
#     pass
# else:
#     if 'pip-delete-this-directory.txt' in fnames:
#         pkgpaths = []
#         for fn in fnames:
#             path = os.path.join(sysbuildpath, fn)
#             if not os.path.isdir(path):
#                 continue
#             path = os.path.abspath(path)
#             pkgpaths.append(path)

#             srcpath = os.path.join(path, 'src')
#             if os.path.isdir(srcpath):
#                 pkgpaths.append(srcpath)

#         for path in pkgpaths:
#             sys.path.insert(0, path)

#         PYTHONPATH = os.environ.get('PYTHONPATH')
#         PATH = ':'.join(pkgpaths)
#         if PYTHONPATH is None:
#             os.environ['PYTHONPATH'] = PATH
#         else:
#             os.environ['PYTHONPATH'] = ':'.join([PATH, PYTHONPATH])


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
