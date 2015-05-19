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

from __future__ import absolute_import

__all__ = ['Path']

from path import Path


class Path(Path):
    """A little wrapper for **path.py** providing a :func:`.samefile` wrapper
       with Windows Python 2 compatibility.
    """
    def samefile(self, other):
        """Also working if there is no ``os.path.samefile()``.
        """
        if not hasattr(self.module, 'samefile'):
            other = Path(other).realpath().normpath().normcase()
            return self.realpath().normpath().normcase() == other
        return self.module.samefile(self, other)
