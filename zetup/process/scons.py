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

"""zetup.process.scons

call scons with updated PYTHONPATH.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['scons']

from . import call


def scons(*args, **options):
    """Call external 'scons' command via :func:`zetup.process.call`,
       which updates PYTHONPATH from current ``sys.path``.

    - All lower_case `options` will be passed as ``**kwargs``
      to :func:`zetup.process.call`.
    - All UPPER_CASE `options` will be passed to the 'scons' command.
    """
    kwargs = {}
    for key, value in list(options.items()):
        if not key.isupper():
            kwargs[key] = options.pop(key)
    return call(
      ['scons'] + list(args) + ['%s=%s' % o for o in options.items()],
      **kwargs)
