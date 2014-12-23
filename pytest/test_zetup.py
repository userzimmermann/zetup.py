"""Test the zetup package.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

import pytest

from inspect import ismodule

from pkg_resources import (
  parse_requirements, get_distribution, DistributionNotFound)

from path import path as Path

import zetup
from zetup import Zetup, find_zetup_config


def test_zetup_config():
    """Test the zetup config management on zetup package's own config.
    """
    zfg = find_zetup_config('zetup')
    assert zfg.NAME == 'zetup'

    pkg_path = Path(zetup.__path__[0]).realpath()

    in_site_packages = ismodule(zfg)
    in_repo = not in_site_packages
    if in_site_packages:
        zfg_path = Path(zfg.__file__).realpath().dirname()
    else:
        zfg_path = Path(zfg.ZETUP_DIR).realpath()

    if in_site_packages:
        assert zfg.__name__ == 'zetup.zetup_config'
        assert zfg_path == pkg_path / 'zetup_config'
    else:
        with pytest.raises(ImportError):
            from zetup import zetup_config

        assert isinstance(zfg, Zetup)
        assert zfg_path == pkg_path.dirname()

    assert zetup.__description__ == zfg.DESCRIPTION

    try:
        dist = get_distribution('zetup')
    except DistributionNotFound:
        if in_repo:
            dist = None
        else:
            raise
    else:
        if in_repo and not Path(dist.location).samefile(pkg_path.dirname()):
            dist = None
    assert zetup.__distribution__ == zfg.DISTRIBUTION.find(pkg_path) \
      == dist

    assert zetup.__version__ == zfg.VERSION

    assert zetup.__requires__ == zfg.REQUIRES
    if in_repo:
        assert list(parse_requirements(zetup.__requires__)) == list(
          parse_requirements((zfg_path / 'requirements.txt').text()))

    for extra in zetup.__extras__:
        assert zetup.__extras__[extra] == zfg.EXTRAS[extra]
        if in_repo:
            assert list(parse_requirements(zetup.__extras__[extra])) \
              == list(parse_requirements(
                   (zfg_path / ('requirements.%s.txt' % extra))
                   .text()))
