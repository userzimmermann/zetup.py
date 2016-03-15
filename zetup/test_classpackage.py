# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014-2016 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""zetup.test_classpackage

pytest unit tests for :class:`zetup.classpackage`.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from __future__ import absolute_import

import zetup


def test_bases():
    for base in [zetup.object, zetup.package]:
        assert issubclass(zetup.classpackage, base)
    for nobase in [zetup.toplevel]:
        assert not issubclass(zetup.classpackage, nobase)


def test_metabases():
    assert type(zetup.classpackage) is zetup.meta


def test__module__():
    assert zetup.classpackage.__module__ == 'zetup'


def test_members():
    # should not contain more members than basic zetup.package
    assert dir(zetup.classpackage) == dir(zetup.package)
