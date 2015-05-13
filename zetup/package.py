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

import os


class Package(str):
    """Package name wrapper with access to
       package path, source files, package data and subpackages.
    """
    def __new__(cls, pkg, root=None, path=None):
        return str.__new__(cls, pkg)

    def __init__(self, pkg, root=None, path=None):
        if isinstance(pkg, Package):
            if not path:
                path = pkg.__dict__.get('path')
            if not root:
                root = pkg.root
        self.root = root or None
        if path:
            self.__dict__['path'] = path

    @property
    def path(self):
        """The absolute path of the package.
        """
        return os.path.realpath(os.path.join(self.root or '.',
          self.__dict__.get('path') or os.path.join(*self.split('.'))))

    def sources(self):
        """Iterates the package's direct source *.py files
           (without sub-package sources).
        """
        for name in os.listdir(self.path):
            path = os.path.join(self.path, name)
            if os.path.isfile(path) and path.endswith('.py'):
                yield path

    def walksources(self):
        """Recursively iterates the source *.py files of the package
           and its sub-packages.
        """
        for path in self.sources():
            yield path
        for pkg in self.subpackages():
            for path in pkg.walksources():
                yield path

    def subpackages(self):
        """Iterates the package's direct sub-package paths
           (without sub-sub-packages).
        """
        for name in os.listdir(self.path):
            path = os.path.join(self.path, name)
            if os.path.isdir(path) and os.path.isfile(
              os.path.join(path, '__init__.py')):
                yield type(self)('.'.join((self, name)))

    def walksubpackages(self):
        for pkg in self.subpackages():
            yield pkg
            for subpkg in pkg.walksubpackages():
                yield subpkg


class Packages(object):
    def __init__(self, toplevel, root=None):
        self.toplevel = list(Package(name, root=root) for name in toplevel)

    def __iter__(self):
        for pkg in self.toplevel:
            yield pkg
            for subpkg in pkg.walksubpackages():
                yield subpkg

    def __len__(self):
        return len(list(iter(self)))

    @property
    def main(self):
        return next(iter(self))

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, repr(self.toplevel))
