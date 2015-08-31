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

import sys
import os
from glob import glob
from textwrap import dedent

if sys.version_info[0] == 3:
    unicode = str

from .error import ZetupError


class ZetupPackageError(ZetupError):
    """Exception related to zetup package config.
    """
    pass


class ZetupPackageCheckError(ZetupPackageError):
    """Exception related to zetup package config.
    """
    def __init__(self, missing, extra):
        self.missing = list(missing)
        self.extra = list(extra)


class File(str):
    """The name of a package file (source or data)
       with reference to the package and its absolute path.
    """
    def __new__(cls, name, package):
        return str.__new__(cls, name)

    def __init__(self, name, package):
        self.package = package

    @property
    def path(self):
        return os.path.join(self.package.path, self)


class Source(File):
    """The name of a package *.py source file
       with reference to the package and its absolute path.
    """
    pass


class DataFile(File):
    """The name of a package data file
       with reference to the package and its absolute path.
    """
    pass


class Package(str):
    """Package name wrapper with access to
       package path, source files, package data and subpackages,
       and validation features for installed packages.
    """
    def __new__(cls, pkg, **kwargs):
        return str.__new__(cls, pkg)

    def __init__(self, pkg, root=None, path=None, data=None,
                 sources=None, datafiles=None, subpackages=None,
                 zfg=None):
        if not isinstance(pkg, Package):
            pkg = None
        self.root = root or pkg and pkg.root
        self._path = path or pkg and pkg._path
        self.data = data and [os.path.sep.join(d.split('/')) for d in data] \
          or pkg and pkg.data or None
        self._sources = sources and list(sources) \
          or pkg and pkg._sources or None
        self._datafiles = datafiles and list(datafiles) \
          or pkg and pkg._datafiles or None
        if not subpackages and pkg:
            subpackages = pkg._subpackages
        self._subpackages = subpackages and [
          type(self)(spkg, root=self.root) for spkg in subpackages
          ] or None
        self.zfg = zfg or pkg and pkg.zfg

    @property
    def path(self):
        """The absolute path of the package.
        """
        return os.path.realpath(os.path.join(self.root or '.',
          self._path or os.path.join(*self.split('.'))))

    def sources(self, force_search=False):
        """Iterates :class:`zetup.package.Source` instances
           of the package's direct source *.py files
           (without sub-package sources).
        """
        if not force_search and self._sources:
            for source in self._sources:
                yield source
            return

        for name in os.listdir(self.path):
            path = os.path.join(self.path, name)
            if os.path.isfile(path) and path.endswith('.py'):
                yield Source(name, package=self)

    def datafiles(self, force_search=False):
        """Iterates :class:`zetup.package.DataFile` instances
           of the package's direct data files
           (without sub-package data files).
        """
        if not force_search and self._datafiles:
            for datafile in self._datafiles:
                yield datafile
            return
        if not self.data:
            return
        for pattern in self.data:
            for path in glob(os.path.join(self.path, pattern)):
                yield DataFile(os.path.relpath(path, self.path),
                               package=self)

    def files(self, force_search=False):
        """Iterates the package's direct sources and data files combined
           (without sub-package files).
        """
        for source in self.sources(force_search=force_search):
            yield source
        for datafile in self.datafiles(force_search=force_search):
            yield datafile

    def subpackages(self, force_search=False):
        """Iterates the package's direct sub-packages as instances of own type
           (without sub-sub-packages).
        """
        if self._subpackages:
            for pkg in self._subpackages:
                yield pkg
            return

        for name in os.listdir(self.path):
            path = os.path.join(self.path, name)
            if os.path.isdir(path) and os.path.isfile(
              os.path.join(path, '__init__.py')):
                yield type(self)('.'.join((self, name)),
                  path=self._path and os.path.join(self._path, name),
                  root=self.root)

    def walk(self):
        """Iterates the package's sub-packages recursively.
        """
        for pkg in self.subpackages():
            yield pkg
            for subpkg in pkg.walk():
                yield subpkg

    def issubpackage(self, parent, recursive=False):
        pkg = self.split('.')
        parent = parent.split('.')
        if len(pkg) <= len(parent):
            return False
        if not recursive and (len(pkg) - len(parent) > 1):
            return False
        return parent == pkg[:len(parent)]

    def __getitem__(self, name):
        """Get a subpackge by its relative name.
        """
        for pkg in self.subpackages():
            if pkg == '.'.join((self, name)):
                return pkg
        raise KeyError("%s has no sub-package named %s"
                       % (repr(self), repr(name)))

    def __getattr__(self, name):
        """Fast interactive way for the shell
           to get a subpackge by its relative name.
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
              "%s has no attribute or sub-package named %s"
              % (repr(self), repr(name)))

    def check(self, raise_=True):
        if self._sources is not None:
            expected = set(self._sources)
            found = set(self.sources(force_search=True))
            diff = expected - found
            if diff:
                if raise_:
                    raise RuntimeError(diff)
                return False

        if self._datafiles is not None:
            expected = set(self._datafiles)
            found = set(self.datafiles(force_search=True))
            diff = expected - found
            if diff:
                if raise_:
                    raise RuntimeError(diff)
                return False

        if self._subpackages is not None:
            expected = set(self._subpackages)
            found = set(self.subpackages(force_search=True))
            diff = expected - found
            if diff:
                if raise_:
                    raise RuntimeError(diff)
                return False

        return True

    @property
    def py(self):
        """Generate Python code for zetup config module.
        """
        return dedent("""
          %s(%s,
            sources=[
              %s
              ],
            subpackages=[
              %s
              ],
            )
          """) % (type(self).__name__, repr(str(self)),
                  ",\n    ".join(repr(os.path.basename(src)) for src in self.sources()),
                  ",\n    ".join(pkg.py for pkg in self.subpackages()))


class Packages(object):
    def _parse(self, text, root=None):
        packages = []
        for line in map(str.strip, text.split('\n')):
            if not line:
                continue
            try:
                pkg, data = map(str.strip, line.split('+'))
            except ValueError:
                pkg, data = line, None
            else:
                data = data.split()
            try:
                pkg, path = map(str.strip, pkg.split(':'))
            except ValueError:
                path = None
            packages.append(Package(pkg, root=root, path=path, data=data))
        toplevel = list(packages)
        for pkg in sorted(packages):
            for item in packages:
                if pkg.issubpackage(item):
                    if item._subpackages:
                        item._subpackages.append(pkg)
                    else:
                        item._subpackages = [pkg]
                        toplevel.remove(pkg)
                    break
        return toplevel

    def __init__(self, text_or_toplevel, root=None, zfg=None):
        self.root = root
        self.zfg = zfg
        if isinstance(text_or_toplevel, (str, unicode)):
            self.toplevel = self._parse(text_or_toplevel, root=root)
        else:
            self.toplevel = [Package(pkg, root=root)
                             for pkg in text_or_toplevel]

    def __iter__(self):
        """Iterate all toplevel and sub-packages.
        """
        for pkg in self.toplevel:
            yield pkg
            for subpkg in pkg.walk():
                yield subpkg

    def __len__(self):
        return len(list(iter(self)))

    def __getitem__(self, name):
        for pkg in self:
            if pkg == name:
                return pkg
        raise KeyError("No package named %s" % repr(name))

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
              "%s instance has no attribute or package named %s"
              % (type(self), repr(name)))

    def __bool__(self):
        """Any packages?
        """
        return bool(self.toplevel)

    #PY2
    def __nonzero__(self):
        return self.__bool__()

    @property
    def main(self):
        return next(iter(self))

    def check(self, raise_=True):
        for pkg in self:
            pkg.check(raise_=raise_)

    @property
    def checked(self):
        self.check()
        return self

    @property
    def py(self):
        """Generate Python code for zetup config module.
        """
        if self.zfg:
            zfg_modname = self.zfg.ZETUP_CONFIG_MODULE
            root_code = "os.path.realpath(__file__)"
            for _ in range(zfg_modname.count('.') + 1):
                root_code = "os.path.dirname(%s)" % root_code
        else:
            root_code = 'None'
        return "%s([\n%s\n  ], root=%s)" % (type(self).__name__,
          ",\n  ".join(pkg.py for pkg in self.toplevel),
          root_code)

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, repr(self.toplevel))
