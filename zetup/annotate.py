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

import sys
import os

from .zetup import find_zetup_config
from .error import ZetupError
from .package import Packages

__all__ = ['annotate', 'annotate_extra']


def annotate(pkgname, check_requirements=True, check_packages=True):
    """Find zetup config for given `pkgname`
       and add __version__, __requires__, __dist__, __description__,
       __packages__ and __extras__ (if defined) to the package object.

    - Automatically checks installed package requirements
      unless `check_requirements` is False.
    - Automatically checks installed package files
      unless `check_packages` is False.
    - Returns the zetup config object.
    """
    try:
        mod = sys.modules[pkgname]
    except KeyError:
        raise ZetupError(
            "Package %s was not found in sys.modules" % repr(pkgname))
    zfg = find_zetup_config(pkgname)
    mod.__version__ = zfg.VERSION
    mod.__requires__ = zfg.REQUIRES
    if check_requirements:
        zfg.REQUIRES.check()
    if zfg.EXTRAS:
        mod.__extras__ = zfg.EXTRAS
    mod.__distribution__ = zfg.DISTRIBUTION.find(os.path.dirname(__file__))
    mod.__description__ = zfg.DESCRIPTION
    mod.__packages__ = zfg.PACKAGES
    if (check_packages
        #TODO: remove (only for backwards compatibility)
        and isinstance(zfg.PACKAGES, Packages)
        ):
        zfg.PACKAGES.check()
    return zfg


def annotate_extra(pkgname, check_requirements=True):
    main, extra = pkgname.rsplit('.', 1)
    mainmod = sys.modules[main]
    mod = sys.modules[pkgname]
    mod.__version__ = mainmod.__version__
    mod.__requires__ = mainmod.__extras__[extra]
    if check_requirements:
        mod.__requires__.check()
