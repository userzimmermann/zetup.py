# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
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

__all__ = ['Zetup', 'find_zetup_config']

import sys
import os

from .zetup import Zetup


# Get zetup's own config:
## try: # from installed zetup package
##     from . import zetup_config as own_config
## except ImportError: # from source
##     own_config = Zetup(os.path.dirname(os.path.realpath(__path__[0])))


def find_zetup_config(modname):
    zfg_modname = modname + '.zetup_config'
    try: # Already imported?
        return sys.modules[zfg_modname]
    except KeyError:
        pass
    try:
        return __import__(zfg_modname).zetup_config
    except ImportError:
        pass
    # ==> no .zetup_config subpackage
    # ==> assume package imported from source (repo)
    # ==> load setup config from package's parent path:
    mod = sys.modules[modname]
    path = os.path.dirname(os.path.dirname(os.path.realpath(mod.__file__)))
    return Zetup(path)


own_config = find_zetup_config(__name__)

__distribution__ = own_config.DISTRIBUTION.find(__path__[0])
__description__ = own_config.DESCRIPTION

__version__ = own_config.VERSION

__requires__ = own_config.REQUIRES # .checked
__extras__ = own_config.EXTRAS

__notebook__ = own_config.NOTEBOOKS['README']


def setup_entry_point(dist, keyword, value):
    """zetup's `entry_point` handler for `setup()` in _setup.py_,
       setting all setup keyword parameters based on zetup config.

    - Activated with `use_setup=True`
    """
    assert keyword == 'use_zetup'
    if not value:
        return

    zetup = Zetup() # reads config from current working directory
                    #  (where setup.py is run)
    keywords = zetup.setup_keywords()
    for name, value in keywords.items():
        # Generally, setting stuff on dist.metadata is enough
        #  (and necessary), but *pip* only works correct
        #  if stuff is also set directly on dist object
        #  (seems to read at least packages list somehow from there):
        for obj in [dist, dist.metadata]:
            setattr(obj, name, value)
