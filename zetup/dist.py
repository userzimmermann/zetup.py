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

__all__ = ['Distribution']

import os
from pkg_resources import (
  get_distribution, DistributionNotFound, VersionConflict)

from .version import Version


class Distribution(str):
    """Simple proxy to get a pkg_resources.Distribution instance
       matching the given name and :class:`Version` instance.
    """
    def __new__(cls, name, pkg, version):
        return str.__new__(cls, name)

    def __init__(self, name, pkg, version):
        """Initialize with distribution `name`, top level `pkg` name
           and `version` string.
        """
        self.pkg = pkg
        self.version = Version(version)

    def find(self, modpath, raise_=True):
        """Try to find the distribution and check version.

        - Also checks if distribution is in the same directory
          as given `modpath`.

        :param raise_: Raise a VersionConflict
          if version doesn't match the given one?
          If false just return None.
        """
        # If no version is given (for whatever reason), just do nothing:
        if not self.version:
            return None
        try:
            dist = get_distribution(self)
        except DistributionNotFound:
            return None
        # check if distribution path matches package path
        if os.path.normcase(os.path.realpath(dist.location)) \
          != os.path.normcase(os.path.dirname(os.path.realpath(modpath))):
            return None
        if dist.parsed_version != self.version.parsed:
            if raise_:
                raise VersionConflict(
                  "Version of distribution %s"
                  " doesn't match %s.__version__ %s."
                  % (dist, self.pkg, self.version))
            return None
        return dist

    @property
    def py(self):
        return '%s(%s, %s, %s)' % (type(self).__name__,
          repr(str(self)), repr(str(self.pkg)), repr(str(self.version)))
