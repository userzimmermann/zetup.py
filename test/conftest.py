"""Common fixtures for zetup tests.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from inspect import ismodule

from zetup import find_zetup_config

import pytest


@pytest.fixture
def zfg():
    """Get zetup's own config.
    """
    return find_zetup_config('zetup')


@pytest.fixture
def in_site_packages():
    """Is zetup imported from repository?
    """
    return ismodule(zfg())


@pytest.fixture
def in_repo():
    """Is zetup imported from site-packages?
    """
    return not in_site_packages()
