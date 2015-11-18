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

from functools import partial

__all__ = ['command']


COMMANDS = {}


def command(func=None, name=None):
    """Decorator for registering basic (non-project-bound) commands.
    """
    if func is None:
        if name:
            return partial(command, name=name)
        raise TypeError(
            "zetup.command.command() decorator "
            "takes at least a function or a name argument.")
    COMMANDS[name or func.__name__] = func
    return func
