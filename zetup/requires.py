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

__all__ = ['Requirements']

import sys
if sys.version_info[0] == 3:
    unicode = str
import re

from pkg_resources import (
  parse_requirements, Requirement,
  get_distribution, DistributionNotFound, VersionConflict)


class Requirements(str):
    """Package requirements manager.
    """
    @staticmethod
    def _parse(text):
        """ Generate parsed requirements from `text`,
            which should contain newline separated requirement specs.

        - Additionally looks for "#import name" comments
          after requirement lines (the actual root module name
          of the required package to use for runtime dependency checks)
          and stores them as .impname attrs on the Requirement instances.
        - Supports #py.. tags at the beginning of lines,
          specifying a python version the requirement applies to.
        """
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            match = re.match(r'^#py([0-9]+) (.*)$', line)
            if match: #==> only required in given python version
                pyver, line = match.groups()
                #TODO:
                # if len(pyver) > 2:
                if not ('%s%s' % sys.version_info[:2]).startswith(pyver):
                    continue
            try:
                req, impname = line.split('#import')
            except ValueError:
                req = next(parse_requirements(line), None)
                impname = req and req.unsafe_name
            else:
                req = next(parse_requirements(req), None)
            if not req: # maybe a comment line
                continue
            req.impname = impname.strip()
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
            txt = reqs
            reqlist = list(cls._parse(reqs))
        else:
            txt = ''
            reqlist = []
            for req in reqs:
                if isinstance(req, (str, unicode)):
                    reqlist.extend(cls._parse(req))
                elif isinstance(req, Requirement):
                    reqlist.append(req)
                else:
                    raise TypeError(type(req))
                txt += '\n%s' % req

        obj = str.__new__(cls, '\n'.join(map(str, reqlist)))
        obj.txt = txt
        obj._list = reqlist
        return obj

    def check(self, raise_=True):
        """Check that all requirements are available (importable)
           and their versions match (using modules' __version__ attributes).

        - Fallback to pkg_resources.get_distribution().version
          if no __version__ or is None.

        :param raise_: Raise DistributionNotFound if ImportError
          or VersionConflict if version doesn't match?
          If False just return False in that case.
        """
        for req in self:
            try:
                mod = __import__(req.impname)
            except ImportError as e:
                if raise_:
                    raise DistributionNotFound(
                      "%s (%s: %s)" % (req, type(e).__name__, e))
                return False
            if not req.specs: # No version constraints
                continue
            try:
                version = mod.__version__
                if version is None:
                    # treat the same as if .__version__ not exists
                    # (handle in following except block)
                    # ==> same exception, just different msg
                    raise AttributeError(
                      "module's '__version__' attribute is None")
            except AttributeError as e_no__version__attr:
                try: # try to get version from distribution
                    dist = get_distribution(req.key)
                except DistributionNotFound as e:
                    if raise_:
                        raise VersionConflict("Need %s. %s: %s. %s: %s" % (
                          req, e_no__version__attr, mod,
                          type(e).__name__, e))
                    return False
                version = dist.version
            if version not in req:
                if raise_:
                    raise VersionConflict(
                      "Need %s. Found %s" % (req, version))
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
        """Return a new :class:`Requirements` instance
           with additional requirements from `text`.
        """
        return type(self)('%s\n%s' % (
          # For simplicity:
          #  Just create explicit #import hints for every requirement:
          ## '\n'.join('%s #import %s' % (req, req.impname) for req in self),
          self.txt,
          text))

    @property
    def py(self):
        return '%s("""\n%s\n""")' % (type(self).__name__, self.txt) ## '\n'.join(
          ## '%s #import %s' % (req, req.impname) for req in self))

    def __repr__(self):
        return str(self)
