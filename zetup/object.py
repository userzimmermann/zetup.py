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
from six import with_metaclass
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


class object(with_metaclass(meta, object)):
    """Basic class derived from builtin ``object``,
       which adds a basic ``__dir__`` method for Python 2.
    """
    if not hasattr(object, '__dir__'):
        def __dir__(self):
            """Get all member names from instance and class level.
            """
            return list(set(chain(self.__dict__, dir(type(self)))))
