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

"""zetup.modules

Module object wrappers for packages, top-level packages,
and top-level packages for extra features.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys
from types import ModuleType
from itertools import chain

from .object import object, meta
from .annotate import annotate, annotate_extra

__all__ = ['package', 'toplevel']


class package(ModuleType, object):
    """Package module object wrapper
       for clean dynamic API import from sub-modules.
    """
    def __init__(self, __name__, __all__=None):
        """Wrap package module given by its `__name__`.

        - Replaces module object in ``sys.modules``.
        - Define the package API by passing a ``dict`` to `__all__`,
          which maps sub-module names (with leading dots)
          to the names of API members defined in those sub-modules.
        - Original package module object is stored in ``self.__module__``.
        """
        ModuleType.__init__(self, __name__)
        self.__name__ = __name__
        self.__module__ = sys.modules[__name__]
        sys.modules[__name__] = self
        self.__dict__['__all__'] = {}
        if __all__ is not None:
            for submodname, members in dict(__all__).items():
                self.__dict__['__all__'].update(
                    (name, submodname) for name in members)

    @property
    def __all__(self):
        """Get API member name list.
        """
        return list(set(chain(
            getattr(self.__module__, '__all__', []),
            self.__dict__['__all__'])))

    def __getattr__(self, name):
        """Dynamically access API from wrapped module
           or import extra API members.
        """
        # first try to get it from package's extra api
        if name in self.__dict__['__all__']:
            submodname = self.__dict__['__all__'][name]
            submod = __import__(self.__name__ + submodname, fromlist=[name])
            submodname = submodname.lstrip('.')
            # was sub-module added to self.__dict__ during __import__?
            if submodname in self.__dict__:
                # ==> move it to original module object to keep API clean
                self.__module__.__dict__[submodname] \
                    = self.__dict__.pop(submodname)
            obj = getattr(submod, name)
            setattr(self, name, obj)
            return obj

        # then try to get attr from wrapper module
        try:
            return getattr(self.__module__, name)
        except AttributeError:
            if name in getattr(self.__module__, '__all__', []):
                raise AttributeError(
                    "%s has no attribute %s although listed in __all__"
                    % (repr(self.__module__), repr(name)))
            else:
                raise AttributeError("%s has no attribute %s"
                                     % (repr(self), repr(name)))

    def __dir__(self):
        """Additionally get all API member names.
        """
        return object.__dir__(self) + self.__all__

    def __repr__(self):
        """Create module-style representation.
        """
        return "<%s %s from %s>" % (
            type(self).__name__, repr(self.__name__),
            repr(self.__module__.__file__))


class toplevel(package):
    """Special top-level package module object wrapper
       for clean dynamic API import from sub-modules
       and automatic application of func:`zetup.annotate`.
    """
    def __init__(self, __name__, __all__=None, check_requirements=True,
                 check_packages=True):
        """Wrap top-level package module given by its `__name__`.

        - See :class:`zetup.package`
          for details about defining the package API.
        - See :func:`zetup.annotate` for details about the extra options.
        """
        super(toplevel, self).__init__(__name__, __all__)
        annotate(__name__, check_requirements=check_requirements,
                 check_packages=check_packages)


class extra_toplevel_meta(meta):
    def __getitem__(cls, extra):
        return type('%s[%s]' % (cls.__name__, extra), (cls, ), {
            'extra': extra,
        })


class extra_toplevel(
        # PY2/3 compatible way to assign metaclass
        extra_toplevel_meta('extra_toplevel_base', (package, ), {})
):
    """Special extra feature top-level package module object wrapper
       for clean dynamic API import from sub-modules
       and automatic application of func:`zetup.annotate_extra`.
    """
    extra = None

    def __init__(self, __name__, __all__, check_requirements=True):
        """Wrap top-level package module given by its `__name__`.

        - See :class:`zetup.package`
          for details about defining the package API.
        - See :func:`zetup.annotate_extra` for details about the extra option.
        """
        package.__init__(self, __name__, __all__)
        annotate_extra(__name__, check_requirements=check_requirements)
