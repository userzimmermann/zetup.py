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

Defines :class:`zetup.classpackage`

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from __future__ import absolute_import

__all__ = ['classpackage']

from importlib import import_module

from .modules import package


class classpackage(package):
    """Sub-package module wrapper, auto-importing a class definition
    from that sub-package and supporting class member definitions
    in separate sub-modules, if:

    * The class is named after the sub-package.
    * The class is a sub-class of :class:`zetup.object`.
    * The sub-package name is defined as API member of parent
      :class:`zetup.package` instance.
    * Sub-module names are listed via ``membermodules=`` argument
      and members in those sub-modules are decorated
      with class method :func:`zetup.object.member`.

    **package/__init__.py** ::

       import zetup
       zetup.package(__name__, ['Class', ...])

    **package/Class/__init__.py** ::

       import zetup
       zetup.classpackage(__name__, membermodules=['methods', ...])

       class Class:
           def __init__(self, ...):
               ...
           ...

    **package/Class/methods.py** ::

       from . import Class

       @Class.member
       def method(self, ...):
           ...

    >>> import package
    >>> package.Class
    <class package.Class>
    >>> package.Class.method
    <function package.Class.method>
    """
    __module__ = __package__

    def __init__(self, pkgname, membermodules=None):
        """Created with ``__name__`` of the subpackage defining the class
        and the optional list of `membermodules` to automatically import
        (sub-modules defining additional class members).
        """
        parentpkgname, classname = pkgname.rsplit('.', 1)
        super(classpackage, self).__init__(pkgname, [classname])

        pkgcls = type(self)
        pkgdict = self.__dict__

        def load_class():
            """Get the actual class object from this class package
            and automatically import all defined ``membermodules``.
            """
            classobj = pkgcls.__getattribute__(self, classname)
            classobj.__module__ = parentpkgname
            if membermodules is not None:
                for modname in membermodules:
                    mod = import_module('%s.%s' % (pkgname, modname))
            return classobj

        class package(type(self)):
            """Help tools like sphinx ``.. autoclass::`` doc generator
            by delegating (almost) all attributes to the actual class object.

            * ``.. autoclass:: package.Class`` first looks up
              ``package.Class`` in imported modules and therefore
              doesn't get the actual class object itself.
            """
            def __getattribute__(self, name):
                if name == classname:
                    # get the actual class object
                    try:
                        return pkgdict[classname]
                    except KeyError:
                        # only load once
                        classobj = pkgdict[classname] = load_class()
                        return classobj
                # only take these few special attributes
                # from the classpackage instance itself
                if name in [
                        '__name__', '__all__',  '__module__', '__path__',
                        '__file__', '__class__', '__dict__',
                ]:
                    return pkgcls.__getattribute__(self, name)
                # and take all other attributes from the class object
                # (by first recursively calling this __getattribute__)
                return getattr(getattr(self, classname), name)

            def __repr__(self):
                return "<%s for %s from %s>" % (
                    pkgcls.__name__, repr(getattr(self, classname)),
                    repr(self.__file__))

        self.__class__ = package
