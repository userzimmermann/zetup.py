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

"""zetup.commands.test

Defines ``zetup test`` command.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import os

from zetup.process import call
from zetup.zetup import Zetup

from zetup.commands.dev import dev


@Zetup.command()
def test(zfg, args=None):
    """Run configured ``test commands``.
    """
    dev(zfg)  # first (re)install project in develop mode
    for command in zfg.TEST_COMMANDS:
        print("zetup: Running %s" % repr(command))
        status = call(command, shell=True, env=os.environ)
        if status:  # ==> error
            return status
