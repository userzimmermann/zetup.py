"""Test :mod:`zetup.object`,
   containing basic ``object``-derived class
   and ``type``-derived ``meta`` class.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from itertools import chain

import zetup


def test_meta():
    """Test basic ``type``-derived :class:``zetup.meta``.
    """
    assert issubclass(zetup.meta, type)

    # check that dir(meta) returns the same as dir(type)
    # (with added '__dir__' in PY2)
    assert set(dir(zetup.meta)) == set(dir(type)).union(['__dir__'])
    # and that there are no duplicate names
    assert sorted(dir(zetup.meta)) == sorted(set(dir(zetup.meta)))


def test_object():
    """Test basic ``object``-derived :class:``zetup.object``.
    """
    assert type(zetup.object) is zetup.meta

    # check that dir(zetup.object) exactly returns all member names
    # from class and metaclass level,
    # which in this case are all members from builtin object and type
    # and the added '__dir__' in PY2 (and auto-added '__weakref__')
    assert set(dir(zetup.object)) \
        == set(chain(dir(object), dir(type), ['__weakref__', '__dir__']))
    # and that there are no duplicate names
    assert sorted(dir(zetup.object)) == sorted(set(dir(zetup.object)))
