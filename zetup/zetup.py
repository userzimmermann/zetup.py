# zetup.py
#
# My common stuff for Python package setups.
#
# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import re
from itertools import chain
from collections import OrderedDict
from subprocess import call
from pkg_resources import (
  get_distribution, parse_version, parse_requirements,
  Requirement, DistributionNotFound, VersionConflict)

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


class Distribution(str):
    """Simple proxy to get a pkg_resources.Distribution instance
       matching the given name and :class:`Version` instance.
    """
    def __new__(cls, name, pkg, version):
        return str.__new__(cls, name)

    def __init__(self, name, pkg, version):
        self.pkg = pkg
        self.version = version

    def find(self, modpath, raise_=True):
        """Try to find the distribution and check version.

        :param raise_: Raise a VersionConflict
          if version doesn't match the given one?
          If false just return None.
        """
        try:
            dist = get_distribution(self)
        except DistributionNotFound:
            return None
        if os.path.realpath(dist.location) \
          != os.path.realpath(os.path.dirname(modpath)):
            return None
        if dist.parsed_version != self.version.parsed:
            if raise_:
                raise VersionConflict(
                  "Version of distribution %s"
                  " doesn't match %s.__version__ %s."
                  % (dist, self.pkg, self.version))
            return None
        return dist


class Version(str):
    """Manage and compare version strings
       using :func:`pkg_resources.parse_version`.
    """
    @staticmethod
    def _parsed(value):
        """Parse a version `value` if needed (if simple string).
        """
        if isinstance(value, (str, unicode)):
            value = parse_version(value)
        return value

    @property
    def parsed(self):
        """The version string as parsed version tuple.
        """
        return parse_version(self)

    # Need to override all the compare methods
    #  (would otherwise be taken from str base)...
    def __eq__(self, other):
        return self.parsed == self._parsed(other)

    def __ne__(self, other):
        return self.parsed != self._parsed(other)

    def __lt__(self, other):
        return self.parsed < self._parsed(other)

    def __le__(self, other):
        return self.parsed <= self._parsed(other)

    def __gt__(self, other):
        return self.parsed > self._parsed(other)

    def __ge__(self, other):
        return self.parsed >= self._parsed(other)


class Requirements(str):
    """Package requirements manager.
    """
    @staticmethod
    def _parse(text):
        """ Generate parsed requirements from `text`,
            which should contain newline separated requirement specs.

        - Additionally looks for "#import modname" comments
          after requirement lines (the actual root module name
          of the required package to use for runtime dependency checks)
          and stores them as .modname attrs on the Requirement instances.
        """
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                req, modname = line.split('#import')
            except ValueError:
                req = next(parse_requirements(line))
                req.modname = req.key
            else:
                req = next(parse_requirements(req))
                req.modname = modname.strip()
            yield req

    def __new__(cls, reqs):
        """Store a list of :class:`pkg_resources.Requirement` instances
           from the given requirement specs
           and additionally store them newline separated
           in the :class:`str` base.

        :param reqs: Either a single string of requirement specs
          or a sequence of strings and/or
          :class:`pkg_resources.Requirement` instances.
        """
        if isinstance(reqs, (str, unicode)):
            reqlist = list(cls._parse(reqs))
        else:
            reqlist = []
            for req in reqs:
                if isinstance(req, (str, unicode)):
                    reqlist.extend(cls._parse(req))
                elif isinstance(req, Requirement):
                    reqlist.append(req)
                else:
                    raise TypeError(type(req))

        obj = str.__new__(cls, '\n'.join(map(str, reqlist)))
        obj._list = reqlist
        return obj

    def check(self, raise_=True):
        """Check that all requirements are available (importable)
           and their versions match (using pkg.__version__).

        :param raise_: Raise DistributionNotFound if ImportError
          or VersionConflict if version doesn't match?
          If False just return False in that case.
        """
        for req in self:
            try:
                mod = __import__(req.modname)
            except ImportError:
                if raise_:
                    raise DistributionNotFound(str(req))
                return False
            if not req.specs: # No version constraints
                continue
            try:
                version = mod.__version__
            except AttributeError as e:
                raise AttributeError("%s: %s" % (e, mod))
            if version not in req:
                if raise_:
                    raise VersionConflict(
                      "Need %s. Found %s" % (str(req), version))
                return False
        return True

    @property
    def checked(self):
        self.check()
        return self

    def __iter__(self):
        return iter(self._list)

    def __getitem__(self, name):
        """Get a requirement by its distribution name.
        """
        for req in self._list:
            if name in [req.key, req.unsafe_name]:
                return req
        raise KeyError(name)

    def __add__(self, text):
        """Return a new manager instance
           with additional requirements from `text`.
        """
        return type(self)('%s\n%s' % (
          # For simplicity:
          #  Just create explicit modname hints for every requirement:
          '\n'.join('%s #import %s' % (req, req.modname) for req in self),
          text))

    def __repr__(self):
        return str(self)


class Extras(OrderedDict):
    """Package extra features/requirements manager.

    - Stores :class:`Requirements` instances by extra feature name keys.
    - Provides an implicit 'all' key, returning a dynamically created
      combined :class:`Requirements` instance with all extra requirements.
    """
    def __setitem__(self, name, text):
        reqs = Requirements(text)
        OrderedDict.__setitem__(self, name, reqs)

    def __getitem__(self, name):
        if name == 'all':
            return Requirements(chain(*self.values()))
        return OrderedDict.__getitem__(self, name)

    def __repr__(self):
        return "\n\n".join((
          "[%s]\n" % key + '\n'.join(map(str, reqs))
            for key, reqs in self.items() if key != 'all'))


try:
    from path import path as Path
except ImportError:
    class Notebook(str):
        pass
else:
    try:
        from IPython import nbconvert
        from jinja2 import BaseLoader, TemplateNotFound
    except ImportError:
        class Notebook(Path):
            pass
    else:
        from inspect import getmembers
        from textwrap import dedent


        def bitbucket_rst_links(rst):
            return re.sub(
              r'<#[0-9.-]+([^>]+)>',
              lambda match: '<#rst-header-%s>' % match.group(1).lower(),
              rst)


        def github_markdown_links(markdown):
            return re.sub(
              r'\[([^\]]+)\]: #(.+)',
              lambda match: '[%s]: #%s' % (
                match.group(1), match.group(2).replace('.', '').lower()),
                markdown)


        class ExtraTemplateLoader(BaseLoader):
            templates = {
              'bitbucket_rst': dedent("""
                {%- extends 'rst.tpl' -%}


                {% block input %}
                {%- if cell.input.strip() -%}

                .. code:: python

                {% if cell.outputs %}
                {{ cell.input | add_prompts(cont='>>> ') | indent }}
                {% else %}
                {{ cell.input | indent }}
                {% endif %}
                {%- endif -%}
                {% endblock input %}


                {% block stream %}
                {{ output.text | indent }}
                {% endblock stream %}


                {% block data_text scoped %}
                {{ output.text | indent }}
                {% endblock data_text %}


                {% block markdowncell scoped %}
                {{ super() | bitbucket_rst_links }}
                {% endblock markdowncell %}
                """),

              'github_markdown': dedent("""
                {%- extends 'markdown.tpl' -%}


                {% block input %}
                ```python
                {% if cell.outputs %}
                {{ cell.input | add_prompts(cont='>>> ') }}
                {% else %}
                {{ cell.input }}
                ```
                {% endif %}
                {% endblock input %}


                {% block stream %}
                {{ output.text }}
                ```
                {% endblock stream %}


                {% block data_text scoped %}
                {{ output.text }}
                ```
                {% endblock data_text %}


                {% block markdowncell scoped %}
                {{ super() | github_markdown_links }}
                {% endblock markdowncell %}
                """),
              }

            def get_source(self, env, template):
                try:
                    return self.templates[template], template, True
                except KeyError:
                    raise TemplateNotFound(template)


        class Notebook(Path):
            EXTRA_FILTERS = {
              'bitbucket_rst_links': bitbucket_rst_links,
              'github_markdown_links': github_markdown_links,
              }

            EXTRA_LOADER = ExtraTemplateLoader()

            def to_bitbucket_rst(self):
                """Export the notebook to Bitbucket optimized reST.

                - Prepends 'rst-header-' to link targets.
                  ('#some-section' --> '#rst-header-some-section')
                """
                rst = nbconvert.export_rst(self,
                  filters=self.EXTRA_FILTERS,
                  extra_loaders=[self.EXTRA_LOADER],
                  # Not a real file,
                  #  will be loaded from string by EXTRA_LOADER:
                  template_file='bitbucket_rst',
                  )[0]
                # bitbucket_rst template puts code cell input and output
                #  in single blocks, but can't prevent empty lines in between
                #==> Remove them:
                return re.sub(
                  # .. code:: python
                  #
                  #     >>> input
                  #
                  #     output
                  r'(\n    >>> .+\n)\s*\n(    [^>])',
                  # .. code:: python
                  #
                  #     >>> input
                  #     output
                  r'\1\2',
                  rst)

            def to_github_markdown(self):
                """Export the notebook to Github optimized Markdown.

                - Removes header enumeration prefixes from link targets.
                  ('#1.-section-one' --> '#section-one')
                """
                markdown = nbconvert.export_markdown(self,
                  filters=self.EXTRA_FILTERS,
                  extra_loaders=[self.EXTRA_LOADER],
                  # Not a real file,
                  #  will be loaded from string by EXTRA_LOADER:
                  template_file='github_markdown',
                  )[0]
                # github_markdown template puts code cell input and output
                #  in single blocks, but can't prevent empty lines in between
                #==> Remove them:
                markdown = re.sub(
                  # ```python
                  # >>> input
                  #
                  # output
                  # ```
                  r'(\n>>> .+\n)\s*\n([^>`])',
                  # ```python
                  # >>> input
                  # output
                  # ```
                  r'\1\2',
                  markdown)
                # And also remove newlines after ```python and before ```:
                markdown = re.sub(r'(\n```python.*\n)\s*', r'\1', markdown)
                markdown = re.sub(r'\n\s*(```\s*\n)', r'\n\1', markdown)
                return markdown


        def _exportmethod(name, func):
            def method(self):
                return func(self)

            method.__name__ = 'to_' + name
            return method


        for name, member in getmembers(nbconvert):
            if name.startswith('export_'):
                name = name.split('_', 1)[1]
                if name != 'by_name':
                    setattr(Notebook, 'to_' + name,
                            _exportmethod(name, member))


class Zetup(object):
    def __init__(self, ZETUP_DIR=None):
        if not ZETUP_DIR:
            # Try to get the directory of this script,
            #  to correctly access VERSION, requirements.txt, ...
            try:
                __file__
            except: # Happens if exec()'d from SConstruct
                ZETUP_DIR = '.'
            else:
                ZETUP_DIR = os.path.realpath(os.path.dirname(__file__))
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
          'cmdclass': SETUP_COMMANDS, # defined below
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

    COMMANDS = ['tox']

    def tox(self):
        tox_ini = 'tox.ini'
        create_tox_ini = not os.path.exists(tox_ini)
        if create_tox_ini:
            with open(tox_ini, 'w') as f:
                f.write(dedent("""
                  [tox]
                  envlist = %s""" % ','.join(
                    'py' + version.replace('.', '')
                    for version in self.PYTHON)
                  + """
                  [testenv]
                  deps =
                    zetup
                  """))
        status = call(['tox'])
        if create_tox_ini:
            os.path.remove(tox_ini)
        return status


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


class PyTest(Command):
    """The setup.py pytest command runs py.test
       with current dir prepended to PYTHONPATH,
       to test package from repo.
    """
    # Must override options handling stuff from Command base...
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """The actual pytest command action called by Command base.
        """
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join([
          os.getcwd(), env.get('PYTHONPATH', '')])
        status = call(['py.test'], env=env)
        if not status:
            sys.exit(status)


class Conda(Command):
    """The setup.py conda command generates meta.yaml and build scripts
       in a .conda subdir and runs conda build .conda

    - Assumes an existing sdist in dist/ for the current package version
      (just use together with sdist command to make sure).
    """
    # Must override options handling stuff from Command base...
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """The actual conda command action called by Command base.
        """
        from path import path as Path
        import yaml

        metadir = Path('.conda')
        metadir.mkdir_p()
        metafile = metadir / 'meta.yaml'
        buildfile = metadir / 'build.sh'

        def conda_req(req):
            """conda wants space between requirement name and version specs.
            """
            return re.sub(r'([=<>]+)', r' \1', str(req))

        requirements = list(map(conda_req, REQUIRES))
        # Also add all extra requirements
        #  (conda doesn't seem to have such an extra features management):
        for extra in EXTRAS.values():
            requirements.extend(map(conda_req, extra))

        meta = { # to be dumped to meta.yaml
          'package': {
            'name': NAME,
            'version': str(VERSION),
            },
          'source': {
            'fn': '%s-%s.tar.gz' % (NAME, VERSION),
            # The absolute path to the sdist in dist/
            'url': 'file://%s' % os.path.realpath(os.path.join(
              'dist', '%s-%s.tar.gz' % (NAME, VERSION)))
            },
          'requirements': {
            'build': [
              'python',
              'pyyaml',
              ] + requirements,
            'run': [
              'python',
              ] + requirements,
            },
          'about': {
            'home': URL,
            'summary': DESCRIPTION,
            },
          }
        with open(metafile, 'w') as f:
            yaml.dump(meta, f, default_flow_style=False)

        with open(buildfile, 'w') as f:
            f.write('#!/bin/bash'
                    '\n\n'
                    '$PYTHON setup.py install'
                    '\n')

        status = call(['conda', 'build', metadir])
        if not status:
            sys.exit(status)


SETUP_COMMANDS = {
  'pytest': PyTest,
  'conda': Conda,
  }


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
