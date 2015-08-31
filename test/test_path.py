"""Test zetup's **path.py** wrapper.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys
import os

WIN = sys.platform.startswith('win')

from path import Path

import zetup


def test_path():
    """Test zetup's **path.py** wrapper using ``__file__``.
    """
    assert issubclass(zetup.Path, Path)
    assert zetup.Path.module is os.path

    # check that Path.samefile() is working if no os.path.samefile exists
    # (like in Windows Python 2.x)
    try:
        samefile_func = os.path.samefile
        delattr(os.path, 'samefile')
    except AttributeError:
        samefile_func = None
    path = zetup.Path(__file__)
    relpath = os.path.relpath(__file__, os.getcwd())
    if WIN: # also check case insensitivity
        path = zetup.Path(path.upper())
        relpath = relpath.lower()
    for relpath in [relpath, Path(relpath), zetup.Path(relpath)]:
        assert path.samefile(relpath)
    if samefile_func:
        os.path.samefile = samefile_func
