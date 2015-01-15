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

__all__ = ['Extras']

from itertools import chain
from collections import OrderedDict

from .requires import Requirements


class Extras(OrderedDict):
    """Package extra features/requirements manager.

    - Stores :class:`Requirements` instances by extra feature name keys.
    - Provides an implicit 'all' key, returning a dynamically created
      combined :class:`Requirements` instance with all extra requirements.
    """
    def __setitem__(self, name, text):
        reqs = Requirements(text)
        OrderedDict.__setitem__(self, name, reqs)

    def __getitem__(self, name):
        if name == 'all':
            return Requirements(chain(*self.values()))
        return OrderedDict.__getitem__(self, name)

    @property
    def py(self):
        return '%s([\n%s\n])' % (type(self).__name__, ',\n'.join(
          '(%s, """\n%s\n""")' % (repr(name), reqs.txt) ## '\n'.join(
            ## '%s #import %s' % (req, req.impname) for req in reqs))
          for name, reqs in self.items()))

    def __repr__(self):
        return "\n\n".join((
          "[%s]\n" % key + '\n'.join(map(str, reqs))
            for key, reqs in self.items() if key != 'all'))
