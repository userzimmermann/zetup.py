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

import os

from zetup.path import Path
from zetup.modules import extra_toplevel


COMMANDS = {}


def command(func):
    """Decorator for registering basic (non-project-bound) commands.
    """
    COMMANDS[func.__name__] = func


@command
def init(name, path=None):
    path = Path(path or os.getcwd())
    with open(path / 'zetuprc', 'w') as f:
        f.write("[%s]\n\n%s\n" % (name, "\n".join("%s =" % key for key in [
          'description',
          'author',
          'url',
          'license',
          'python',
          'classifiers',
          'keywords',
          ])))


extra_toplevel(__name__, __all__={
    '.error': ['ZetupCommandError'],
    '.make': ['ZetupMakeError', 'make'],
    '.run': ['run'],
    '.pytest': ['pytest'],
    '.tox': ['tox'],
    '.conda': ['conda'],
})
