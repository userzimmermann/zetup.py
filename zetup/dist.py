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

from __future__ import absolute_import, print_function

import os

import pkg_resources
from pkg_resources import (
  get_distribution, DistributionNotFound, VersionConflict)

from .version import Version

__all__ = ['Distribution']


class Distribution(str):
    """Simple proxy to get a pkg_resources.Distribution instance
       matching dist name and version from a zetup config object.
    """
    def __new__(cls, zfg_or_name, mainpkg=None, version=None):
        if isinstance(zfg_or_name, str):
            name = zfg_or_name
        else:
            name = zfg_or_name.NAME
        return str.__new__(cls, name)

    def __init__(self, zfg_or_name, mainpkg=None, version=None):
        """Initialize with zetup config in `zfg_or_name`.

        - Supports dist name as first argument
          and remaining arguments for backwards compatibility.
        """
        if not isinstance(zfg_or_name, str):
            self.zfg = zfg_or_name
        else:
            self.zfg = None
            self.__dict__['version'] = version and Version(version)

    @property
    def version(self):
        """Get version from zetup config as :class:`zetup.Version` instance.
        """
        # first look for explicit version from __init__
        # for backwards compatibility
        return self.__dict__.get('version') \
            or self.zfg.VERSION and Version(self.zfg.VERSION)

    def find(self, modpath, raise_=True):
        """Try to find the distribution and check version.

        - Also checks if distribution is in the same directory
          as given `modpath`.
        - Automatically reinstalls zetup in develop mode
          on distribution version mismatch
          if handling zetup's own config from zetup's project src.

        :param raise_:
           Raise a ``VersionConflict``
           if version doesn't match the given one?
           If ``False`` just return ``None``.
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
            message = (
                "Version of distribution %s "
                "doesn't match version %s from %s. "
                % (repr(dist), self.version, repr(self.zfg)))
            # are we handling zetup's own config?
            if self == 'zetup':
                from zetup.zetup import Zetup
                # and was it loaded from zetup's project src?
                if isinstance(self.zfg, Zetup):
                    print('zetup:', message)
                    # then automatically reinstall zetup in develop mode
                    print('zetup: Reinstalling in develop mode...')
                    import zetup.commands.dev
                    self.zfg.dev()
                    # reset setuptools distribution cache
                    pkg_resources.working_set = pkg_resources.WorkingSet(
                        pkg_resources.working_set.entries)
                    # and return updated dist
                    return get_distribution(self)

            elif raise_:
                raise VersionConflict(
                    message + "Please reinstall %s." % str.__repr__(self))
            return None
        return dist

    @property
    def py(self):
        return '%s(zfg)' % (type(self).__name__)
