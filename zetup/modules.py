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
from warnings import warn
from inspect import ismodule
from types import ModuleType
from itertools import chain

from .object import object, meta
from .annotate import annotate, annotate_extra

__all__ = ['package', 'toplevel']


class deprecated(str):
    def __repr__(self):
        return "deprecated(%s)" % str.__repr__(self)


class package(ModuleType, object):
    """Package module object wrapper
       for clean dynamic API import from sub-modules.
    """
    def __init__(self, name, api=None, aliases=None,
                 deprecated_aliases=None):
        """Wrap package module given by its `name` and `api` member list.

        - Replaces original module object in ``sys.modules``.
        - Define the package API by passing a ``dict`` to `all`,
          which maps module names or own sub-modules (with leading dot)
          to the names of API members defined in those (sub-)modules.
        - Original package module object is stored in :attr:``.__module__``.
        """
        mod = sys.modules[name]
        ModuleType.__init__(self, name, mod.__doc__)
        self.__name__ = name
        self.__module__ = mod
        sys.modules[name] = self
        self.__dict__['__all__'] = api \
            = dict.fromkeys(api) if api is not None else {}
        if aliases is not None:
            api.update(aliases)
        if deprecated_aliases is not None:
            api.update((deprecated(alias), name)
                       for alias, name in dict(deprecated_aliases).items())
        # if api is not None:
        #     for submodname, members in dict(__all__).items():
        #         self.__dict__['__all__'].update(
        #             (name, submodname) for name in members)

    @property
    def __all__(self):
        """Get API member name list (without deprecated aliases).
        """
        return list(set(chain(
            getattr(self.__module__, '__all__', ()),
            (name for name in self.__dict__['__all__']
             if not isinstance(name, deprecated)))))

    def __setattr__(self, name, value):
        """Prevent submodules from being added as attributes
           to avoid unnecessary ``dir()`` pollution.
        """
        if ismodule(value) and (
                value.__name__ == '%s.%s' % (self.__name__, name)
                and not isinstance(value, package)
        ):
            return
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        """Dynamically access API from wrapped module
           or import extra API members.
        """
        # # first try to get it from package's extra api
        # if name in self.__dict__['__all__']:
        #     submodname = self.__dict__['__all__'][name]
        #     submod = __import__(self.__name__ + submodname, fromlist=[name])
        #     submodname = submodname.lstrip('.')
        #     # was sub-module added to self.__dict__ during __import__?
        #     if submodname in self.__dict__:
        #         # ==> move it to original module object to keep API clean
        #         self.__module__.__dict__[submodname] \
        #             = self.__dict__.pop(submodname)
        #     obj = getattr(submod, name)
        #     setattr(self, name, obj)
        #     return obj

        realname = self.__dict__['__all__'].get(name)
        if realname is not None:
            if isinstance(name, deprecated):
                warn("%s.%s is deprecated in favor of %s.%s"
                     % (self.__name__, name, self.__name__, realname),
                     DeprecationWarning)
            name = realname
        # # then try to get attr from wrapper module
        try:
            return getattr(self.__module__, name)
        except AttributeError:
            if name in getattr(self.__module__, '__all__', ()):
                raise AttributeError(
                    "%s has no attribute %s although listed in __all__"
                    % (repr(self.__module__), repr(name)))
            else:
                try:
                    return sys.modules['%s.%s' % (self.__name__, name)]
                except KeyError:
                    raise AttributeError("%s has no attribute %s"
                                         % (repr(self), repr(name)))

    def __dir__(self):
        """Additionally get all API member names.
        """
        def exclude():
            """Get names of submodules which were implicitly added
               to this package wrapper's ``__dict__``
               by ``from .submodule import ...`` statements in wrapped module
               following the wrapper instantiation.
            """
            for name, obj in self.__dict__.items():
                if name.startswith('__'):
                    continue
                if ismodule(obj) and not isinstance(obj, package):
                    yield name

        return list(chain(
            # (name for name in self.__module__.__dict__ if name.startswith('__')),
            set(object.__dir__(self)).difference(exclude()),
            self.__all__))

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
    def __init__(self, name, api=None,
                 aliases=None, deprecated_aliases=None,
                 check_requirements=True, check_packages=True):
        """Wrap top-level package module given by its `name`
           and `api` member list.

        - See :class:`zetup.package`
          for details about defining the package API.
        - See :func:`zetup.annotate` for details about the check options.
        """
        super(toplevel, self).__init__(
            name, api, aliases=aliases,
            deprecated_aliases=deprecated_aliases)
        annotate(name, check_requirements=check_requirements,
                 check_packages=check_packages)


class extra_toplevel_meta(meta):
    extra = None

    def __getitem__(cls, extra):
        mcs = type(cls)
        meta = type('%s[%s]' % (mcs.__name__, extra), (mcs, ), {
            'extra': extra,
        })
        return meta('%s[%s]' % (cls.__name__, extra), (cls, ), {})


class extra_toplevel(
        # PY2/3 compatible way to assign metaclass
        extra_toplevel_meta('extra_toplevel_base', (package, ), {})
):
    """Special extra feature top-level package module object wrapper
       for clean dynamic API import from sub-modules
       and automatic application of func:`zetup.annotate_extra`.
    """
    def __init__(self, toplevel, name, api=None,
                 aliases=None, deprecated_aliases=None,
                 check_requirements=True):
        """Wrap top-level package module given by its `name`
           and `api` member list.

        - See :class:`zetup.package`
          for details about defining the package API.
        - See :func:`zetup.annotate_extra` for details about the extra option.
        """
        super(extra_toplevel, self).__init__(
            name, api, aliases=aliases,
            deprecated_aliases=deprecated_aliases)
        extra = type(self).extra
        annotate_extra[extra](
            toplevel, name, check_requirements=check_requirements)
