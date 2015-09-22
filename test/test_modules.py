"""Test :mod:`zetup.modules`,
   containing the (top-level) package module object wrappers.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from inspect import ismodule
from types import ModuleType

import zetup


def test_zetup_toplevel(zfg, in_repo, in_site_packages):
    """Test :class:`zetup.modules.toplevel` via Zetup's own top-level package.
    """
    assert ismodule(zetup)
    assert isinstance(zetup, zetup.toplevel)

    # is the original zetup module correctly stored?
    assert type(zetup.__module__) is ModuleType
    assert zetup.__module__.__name__ == 'zetup'
    # and does __getattr__ delegation work?
    assert zetup.__file__ is zetup.__module__.__file__
    assert zetup.__path__ is zetup.__module__.__path__

    # the dynamic 'zetup.toplevel' member import above
    # should NOT result in the 'zetup.modules' sub-module
    # being added to the wrapper's __dict__
    assert 'modules' not in zetup.__dict__
    assert 'modules' not in dir(zetup)
    # instead it should end up in the original module's __dict__
    assert 'modules' in zetup.__module__.__dict__
