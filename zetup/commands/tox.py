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

import os
from textwrap import dedent
from subprocess import call

from zetup import Zetup


@Zetup.command
def tox(self):
    tox_ini = 'tox.ini'
    create_tox_ini = not os.path.exists(tox_ini)
    if create_tox_ini:
        with open(tox_ini, 'w') as f:
            f.write(dedent("""
              [tox]
              envlist = %s""" % ','.join(
                'py' + version.replace('.', '')
                for version in self.PYTHON)
              + """
              [testenv]
              deps =
                zetup
              """))
    status = call(['tox'])
    if create_tox_ini:
        os.path.remove(tox_ini)
    return status
