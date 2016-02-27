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

"""zetup.classpackage

* Defines :class:`zetup.classpackage`

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['classpackage']

from importlib import import_module

from .modules import package


class classpackage(package):
    """Subpackage module wrapper for auto-importing a class from a subpackage
    if class is named after subpackage and subpackage name is defined
    as API member of parent package.
    """
    __module__ = __package__

    def __init__(self, pkgname, membermodules=None):
        """Created with ``__name__`` of the subpackage defining the class
        and on optional list of `membermodules`,
        which contain additional class members named after those submodules.
        """
        clsname = pkgname.rsplit('.', 1)[-1]
        package.__init__(self, pkgname, [clsname])
        self.membermodules = membermodules

    def __getattr__(self, name):
        """Automatically import all ``.membermodules``
        and add contained class members to class object
        if it is requested the first time.
        """
        obj = package.__getattr__(self, name)
        clsname = self.__all__[0]
        if name == clsname:
            pkgname = obj.__module__ = self.__name__.rsplit('.', 1)[0]
            if self.membermodules is not None:
                for membername in self.membermodules:
                    mod = import_module('%s.%s' % (
                        self.__name__, membername))
                    member = getattr(mod, membername)
                    member.__module__ = pkgname
                    member.__qualname__ = '%s.%s' % (
                        obj.__name__, membername)
                    setattr(obj, membername, member)
            # store class object as classpackage attribute
            # to avoid __getattr__ getting called again
            setattr(self, clsname, obj)
        return obj
