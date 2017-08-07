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
from .resolve import resolve
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
    'resolve', 'DistributionNotFound', 'VersionConflict',
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
    """
    Zetup's ``entry_point`` handler for the ``setup()`` process in a project's
    **setup.py**, setting all setup keyword parameters based on zetup config

    Activated with ``setup(setup_requires=['zetup'], use_zetup=True)``
    """
    assert keyword == 'use_zetup'
    if not value:
        return

    from .zetup import Zetup
    # read config from current working directory (where setup.py is run)
    zetup = Zetup()
    keywords = zetup.setup_keywords()
    for name, value in keywords.items():
        # generally, setting stuff on dist.metadata is enough (and necessary)
        setattr(dist.metadata, name, value)
        # but *pip* only works correct if some stuff is also set directly on
        # dist object (pip seems to read at least package infos somehow from
        # there)
        if name.startswith('package') or name.endswith('requires'):
            setattr(dist, name, value)

    # finally run any custom setup hooks defined in project's zetup config
    if zetup.SETUP_HOOKS:
        sys.path.insert(0, '.')
        for hook in zetup.SETUP_HOOKS:
            modname, funcname = hook.split(':')
            mod = __import__(modname)
            for subname in modname.split('.')[1:]:
                mod = getattr(mod, subname)
            func = getattr(mod, funcname)
            func(dist)

    if not zetup.in_repo:
        # ==> setup was run from distribution ==> no files need to be made
        return

    # resolve requirements for zetup make
    resolve(['zetup[commands]>={}'.format(__import__('zetup').__version__)])
    import zetup.commands as _

    # make necessary files and store make result globally, so that files are
    # removed on exit via Made.__del__
    global MADE
    make_targets = ['VERSION', 'setup.py', 'zetup_config']
    MADE = zetup.make(targets=make_targets)
