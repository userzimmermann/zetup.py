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

"""zetup.conda

Provides a convenience ``conda`` interface to external conda executable.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from __future__ import absolute_import

import os
from subprocess import PIPE
import json

from zetup.process import Popen, call
from zetup.object import object

__all__ = ['conda']


class Conda(object):
    """Creates an interface to external conda executable.
    """
    def __init__(self, command=None):
        """Implicitly use the optional conda `command`
           as first conda argument.
        """
        self.command = command

    def __call__(self, *args, **options):
        """Runs external conda executable with the given `args`.

        - Automatically adds ``--json`` arg
          and returns pythonized JSON output.
        - If called with ``json=False``,
          stdout is not captured and status code is returned.
        """
        args = list(args)
        if self.command:
            args.insert(0, self.command)
        if options.get('json', True):
            return json.loads(Popen(
                ['conda'] + args + ['--json'], env=os.environ,
                stdout=PIPE, universal_newlines=True
            ).communicate()[0])
        return call(['conda'] + args, env=os.environ)

    def __getattr__(self, command):
        """Get an interface for a specific conda `command`.
        """
        if command.startswith('_'):
            raise AttributeError("%s has no attribute %s"
                                 % (repr(self), repr(command)))
        return type(self)(command)


# the actual conda interface
conda = Conda()
