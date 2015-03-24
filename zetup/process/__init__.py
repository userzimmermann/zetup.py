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

subprocess wrappers for calling external programs with updated PYTHONPATH.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['call', 'Popen']

import sys
import os
import subprocess


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


def call(command, **kwargs):
    """Wrapper for :func:`subprocess.call`,
       which updates PYTHONPATH from current ``sys.path``.
    """
    _prepare_kwargs(kwargs)
    return subprocess.call(command, **kwargs)


class Popen(subprocess.Popen):
    """Wrapper for :class:`subprocess.Popen`,
       which updates PYTHONPATH from current ``sys.path``.
    """
    def __init__(self, command, **kwargs):
        _prepare_kwargs(kwargs)
        subprocess.Popen.__init__(self, command, **kwargs)
