"""Common fixtures for zetup tests.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from zetup import find_zetup_config

import pytest


@pytest.fixture
def zfg():
    """Get zetup's own config.
    """
    return find_zetup_config('zetup')
