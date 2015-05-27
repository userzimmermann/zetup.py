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

"""zetup.process

subprocess wrappers for calling external programs with updated PYTHONPATH
and better Windows support by implicitly calling .bat and .cmd scripts
without explicitly specified file extension.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['call', 'Popen']

import sys
import os
from itertools import chain
import subprocess

if sys.version_info[0] == 3:
    unicode = str


# define a platform-dependent `_command` helper,
# which converts a `command` arg for subprocess.Popen or .call
# to support Windows .bat and .cmd scripts without extension
if sys.platform.startswith('win'):
    try:
        # find script path with win32api.FindExecutable()
        # if pywin32 is installed
        import win32api
    except ImportError:
        # otherwise run through cmd.exe /c (same as shell=True)
        def _command(command, kwargs):
            if kwargs.get('shell'):
                return command
            if isinstance(command, (str, unicode)):
                return "cmd /c " + command
            return chain(('cmd', '/c'), command)
    else:
        def _command(command, kwargs):
            if kwargs.get('shell'):
                return command
            if isinstance(command, (str, unicode)):
                command, args = command.split(None, 1)
                status, path = win32api.FindExecutable(command)
                return " ".join((path, args))
            command = iter(command)
            status, path = win32api.FindExecutable(next(command))
            return chain((path, ), command)

else: # no Windows ==> just pass through
    def _command(command, kwargs):
        return command


def _prepare_kwargs(kwargs):
    """Prepare (manipulate) the given `kwargs` dict for passing to
       :func:`subprocess.call` or :class:`subprocess.Popen`
       by resolving any zetup-specific stuff.
    """
    env = kwargs.get('env')
    if env is None:
        env = kwargs['env'] = dict(os.environ,
          PYTHONPATH=os.pathsep.join(sys.path))

    env.update(kwargs.pop('env_update', {}))
    for key, value in kwargs.pop('env_defaults', {}).items():
        env.setdefault(key, value)


class Popen(subprocess.Popen):
    """Wrapper for :func:`subprocess.Popen`,
       which updates PYTHONPATH from current ``sys.path``.

    - Supports same `kwargs` as ``subprocess`` implementation.
    - Setting ``env=`` overrides whole environment;
      to keep PYTHONPATH update, use ``env_update=`` and ``env_defaults=``
      with dicts containing only the variables to change.
    - On Windows, supports running scripts without explicitly adding
      ``'.bat'`` or ``'.cmd'`` extensions.
      **pywin32** should be installed for better performance.
    """
    def __init__(self, command, **kwargs):
        _prepare_kwargs(kwargs)
        command = _command(command, kwargs)
        subprocess.Popen.__init__(command, **kwargs)


def call(command, **kwargs):
    _prepare_kwargs(kwargs)
    command = _command(command, kwargs)
    return subprocess.call(command, **kwargs)

call.__doc__ = Popen.__doc__.replace('Popen', 'call')
