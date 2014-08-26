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

__all__ = ['Zetup', 'COMMANDS']

# Import zetup script to get zetup's own setup data:
# from . import zetup


# z = zetup.Zetup()

# ## __distribution__ = zetup.DISTRIBUTION.find(__path__[0])
# __description__ = z.DESCRIPTION

# __version__ = z.VERSION

# __requires__ = z.REQUIRES.checked
# __extras__ = z.EXTRAS

# __notebook__ = z.NOTEBOOKS['README']


from .zetup import Zetup
from . import commands


COMMANDS = commands.__all__
