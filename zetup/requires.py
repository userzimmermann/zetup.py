# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

__all__ = ['Requirements']

from pkg_resources import (
  parse_requirements, Requirement,
  DistributionNotFound, VersionConflict)


class Requirements(str):
    """Package requirements manager.
    """
    @staticmethod
    def _parse(text):
        """ Generate parsed requirements from `text`,
            which should contain newline separated requirement specs.

        - Additionally looks for "#import modname" comments
          after requirement lines (the actual root module name
          of the required package to use for runtime dependency checks)
          and stores them as .modname attrs on the Requirement instances.
        """
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                req, modname = line.split('#import')
            except ValueError:
                req = next(parse_requirements(line))
                req.modname = req.key
            else:
                req = next(parse_requirements(req))
                req.modname = modname.strip()
            yield req

    def __new__(cls, reqs):
        """Store a list of :class:`pkg_resources.Requirement` instances
           from the given requirement specs
           and additionally store them newline separated
           in the :class:`str` base.

        :param reqs: Either a single string of requirement specs
          or a sequence of strings and/or
          :class:`pkg_resources.Requirement` instances.
        """
        if isinstance(reqs, (str, unicode)):
            reqlist = list(cls._parse(reqs))
        else:
            reqlist = []
            for req in reqs:
                if isinstance(req, (str, unicode)):
                    reqlist.extend(cls._parse(req))
                elif isinstance(req, Requirement):
                    reqlist.append(req)
                else:
                    raise TypeError(type(req))

        obj = str.__new__(cls, '\n'.join(map(str, reqlist)))
        obj._list = reqlist
        return obj

    def check(self, raise_=True):
        """Check that all requirements are available (importable)
           and their versions match (using pkg.__version__).

        :param raise_: Raise DistributionNotFound if ImportError
          or VersionConflict if version doesn't match?
          If False just return False in that case.
        """
        for req in self:
            try:
                mod = __import__(req.modname)
            except ImportError:
                if raise_:
                    raise DistributionNotFound(str(req))
                return False
            if not req.specs: # No version constraints
                continue
            try:
                version = mod.__version__
            except AttributeError as e:
                raise AttributeError("%s: %s" % (e, mod))
            if version not in req:
                if raise_:
                    raise VersionConflict(
                      "Need %s. Found %s" % (str(req), version))
                return False
        return True

    @property
    def checked(self):
        self.check()
        return self

    def __iter__(self):
        return iter(self._list)

    def __getitem__(self, name):
        """Get a requirement by its distribution name.
        """
        for req in self._list:
            if name in [req.key, req.unsafe_name]:
                return req
        raise KeyError(name)

    def __add__(self, text):
        """Return a new manager instance
           with additional requirements from `text`.
        """
        return type(self)('%s\n%s' % (
          # For simplicity:
          #  Just create explicit modname hints for every requirement:
          '\n'.join('%s #import %s' % (req, req.modname) for req in self),
          text))

    def __repr__(self):
        return str(self)
