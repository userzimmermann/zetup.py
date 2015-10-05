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

"""zetup.commands.dev

Defines ``zetup dev`` command.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys
import os

import pkg_resources
import pip

from path import Path

from zetup.zetup import Zetup
from zetup.conda import conda

__all__ = ['dev']


@Zetup.command(depends=['setup.py'])
def dev(zfg, args=None):
    """Install project in develop mode.
    """
    # first remove any current project installation
    try:  # check for conda
        conda_info = conda.info()
    except OSError:  # ==> no conda
        pass
    else:
        # are we in a conda environment?
        if any(Path(conda_info[key]).samefile(sys.prefix)
               for key in ['root_prefix', 'default_prefix']
        # and is project installed via conda?
        ) and conda.list('--no-pip', '--full-name', zfg.NAME):
            # then also remove it via conda
            status = conda.remove(zfg.NAME, json=False)
            if status:  # ==> error
                return status
    # is there some project (develop) install (left) to be removed via pip?
    while True:
        try:
            # always use a refreshed working set
            # (interface to installed python package distributions)
            dist = pkg_resources.WorkingSet().by_key[zfg.NAME]
        except KeyError:  # ==> nothing left to uninstall
            break
        status = pip.main(['uninstall', zfg.NAME, '--yes'])
        if status:  # ==> error
            return status
        if Path(dist.location).samefile(zfg.ZETUP_DIR):
            # pip doesn't remove local .egg-info/ dirs of develop installs
            egg_info = Path(dist._provider.egg_info).realpath()
            print("zetup: Removing %s%s" % (egg_info, os.path.sep))
            egg_info.rmtree()
    # finally (re)install project in develop mode (and return pip status code)
    return pip.main(['install', '--editable', zfg.ZETUP_DIR])
