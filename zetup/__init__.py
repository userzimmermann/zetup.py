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

"""zetup

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from __future__ import absolute_import

import sys

import pkg_resources
#HACK: happens on setup of namespace packages
if pkg_resources.require is None:
    # might be needed by package requirements
    pkg_resources.require = pkg_resources.WorkingSet().require


from .zetup import Zetup, find_zetup_config
from .error import ZetupError
from .config import ZetupConfigNotFound
from .requires import DistributionNotFound, VersionConflict
from .process import Popen, call
from .object import object, meta
from .annotate import annotate
from .modules import package, toplevel, extra_toplevel
from .classpackage import classpackage
# import notebook subpackage for defining extra_toplevel below
from . import notebook


zetup = toplevel(__name__, [
    'Zetup', 'find_zetup_config',
    'ZetupError', 'ZetupConfigNotFound',
    'DistributionNotFound', 'VersionConflict',
    'Popen', 'call',
    'object', 'meta',
    'annotate', 'package', 'toplevel', 'extra_toplevel',
], check_requirements=False)

# can't be defined in .notebook subpackage
# because .notebook is also needed to load zetup's own config
# which is required for making extra_toplevel instantiation work
extra_toplevel(zetup, notebook.__name__, [
    'Notebook',
], check_requirements=False)
# since actual .notebook subpackage was imported before
# a manually setting of the subpackage attribute
# on the zetup toplevel wrapper is needed
sys.modules[__name__].notebook = sys.modules[notebook.__name__]


def setup_entry_point(dist, keyword='use_zetup', value=True):
    """Zetup's ``entry_point`` handler for ``setup()``
       in a project's **setup.py**, setting all setup keyword parameters
       based on zetup config.

    - Activated with ``setup(setup_requires=['zetup'], use_zetup=True)``
    """
    assert keyword == 'use_zetup'
    if not value:
        return

    from .zetup import Zetup
    zetup = Zetup() # reads config from current working directory
                    # (where setup.py is run)
    keywords = zetup.setup_keywords()
    for name, value in keywords.items():
        # Generally, setting stuff on dist.metadata is enough
        # (and necessary), but *pip* only works correct
        # if stuff is also set directly on dist object
        # (seems to read at least packages list somehow from there):
        for obj in [dist, dist.metadata]:
            setattr(obj, name, value)

    # finally run any custom setup hooks defined in project's zetup config,
    # but first check setup requirements
    if zetup.SETUP_REQUIRES:
        zetup.SETUP_REQUIRES.check()
    if zetup.SETUP_HOOKS:
        sys.path.insert(0, '.')
        for hook in zetup.SETUP_HOOKS:
            modname, funcname = hook.split(':')
            mod = __import__(modname)
            for subname in modname.split('.')[1:]:
                mod = getattr(mod, subname)
            func = getattr(mod, funcname)
            func(dist)
