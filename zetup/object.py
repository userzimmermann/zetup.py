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

"""zetup.object

Basic ``object``-derived class and ``type``-derived ``meta`` class
with some added features.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from itertools import chain

__all__ = ['object', 'meta']


class meta(type):
    """Basic metaclass derived from builtin ``type``,
       which adds a unified basic ``__dir__`` method for Python 2 and 3,
       which always returns all member names from metaclass and class level.
    """
    if hasattr(type, '__dir__'):  # PY3
        def __dir__(cls):
            """Get all member names from class and metaclass level.
            """
            return list(set(chain(type.__dir__(cls), dir(type(cls)))))

    else:  # PY2
        def __dir__(cls):
            """Get all member names from class and metaclass level.
            """
            return list(set(chain(
                dir(type(cls)), *(c.__dict__ for c in cls.mro()))))

    @classmethod
    def metamember(mcs, obj):
        """Decorator for adding `obj` as a member
        to the metaclass of this class ::

           class Meta(zetup.meta):
               ...

           class Class(zetup.object, metaclass=Meta):
               ...

           @Class.metamember
           def method(cls, ...):
               ...

        >>> Meta.method
        <function Meta.method>
        >>> Class.method
        <bound method Meta.method of Class>
        """
        if isinstance(obj, property):
            name = obj.fget.__name__
        else:
            try:
                name = obj.__name__
            except AttributeError:
                name = obj.__func__.__name__
            else:
                obj.__qualname__ = '%s.%s' % (
                    getattr(mcs, '__qualname__', mcs.__name__),
                    obj.__name__)
        setattr(mcs, name, obj)
        return obj

    def member(cls, obj):
        """Decorator for adding `obj` as a member to this class ::

           class Class(zetup.object):
               ...

           @Class.member
           def method(self, ...):
               ...

        >>> Class.method
        <function Class.method>
        """
        if isinstance(obj, property):
            name = obj.fget.__name__
        else:
            try:
                name = obj.__name__
            except AttributeError:
                name = obj.__func__.__name__
            else:
                obj.__qualname__ = '%s.%s' % (
                    getattr(cls, '__qualname__', cls.__name__),
                    obj.__name__)
        setattr(cls, name, obj)
        return obj


# PY2/3 compatible way to create class `object` with metaclass `meta`
clsattrs = {
    '__doc__':
    """Basic class derived from builtin ``object``,
       which adds a basic ``__dir__`` method for Python 2.
    """}
if not hasattr(object, '__dir__'):
    def __dir__(self):
        """Get all member names from instance and class level.
        """
        return list(set(chain(
            self.__dict__, *(c.__dict__ for c in type(self).mro()))))

    clsattrs['__dir__'] = __dir__

object = meta('object', (object, ), clsattrs)
