# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014-2016 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""zetup.doc

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys
from importlib import import_module
from types import ModuleType

import zetup

# zetup.package(__name__, ['AutoDocScopeImporter'])


class AutoDocScopeModule(ModuleType):

    # to be accepted as packages for subscope imports :)
    __path__ = None

    def __init__(self, name, scope):
        ModuleType.__init__(self, scope.__name__)
        modclass = type(self)

        class Module(type(self)):

            def __getattribute__(self, name):
                if name in ['__class__', '__path__']:
                    return modclass.__getattribute__(self, name)
                return getattr(scope, name)

            def __repr__(self):
                return "<%s for %s>" % (modclass.__name__, repr(scope))

        self.__class__ = Module


class AutoDocScopeImporter(object):

    def __init__(self, pkgname):
        package = import_module(pkgname)
        if not isinstance(package, zetup.package):
            raise TypeError("%s is not a zetup.package instance"
                            % repr(package))
        self.package = package

    def find_module(self, name, path):
        if name.startswith(self.package.__name__ + '.'):
            return self

    def load_module(self, name):
        assert name.startswith(self.package.__name__ + '.')
        scope = scopemod = self.package
        for attr in name[len(self.package.__name__) + 1:].split('.'):
            scope = getattr(scope, attr)
            scopemod = AutoDocScopeModule(
                '%s.%s' % (scopemod.__name__, attr), scope)
            scopemod.__path__ = None
            sys.modules[name] = scopemod
        return scope

    # def __repr__(self):
    #     return "<%s for %s>" % (type(self).__name__, repr(self.module))
