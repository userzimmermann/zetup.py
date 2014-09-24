from inspect import ismodule

from pkg_resources import get_distribution

from path import path as Path

from pytest import raises

import zetup
from zetup import Zetup, find_zetup_config


def test_zetup():
    zfg = find_zetup_config('zetup')
    assert zfg.NAME == 'zetup'

    pkg_path = Path(zetup.__path__[0]).realpath()
    zfg_path = Path(zfg.ZETUP_DIR).realpath()

    in_site_packages = ismodule(zfg)
    in_repo = not in_site_packages

    if in_site_packages:
        assert zfg.__name__ == 'zetup.zetup_config'
        assert zfg_path == pkg_path / 'zetup_config'
    else:
        with raises(ImportError):
            from zetup import zetup_config
        assert isinstance(zfg, Zetup)
        assert zfg_path == pkg_path.dirname()

    assert zetup.__description__ == zfg.DESCRIPTION

    dist = get_distribution('zetup')
    if in_repo and not Path(dist.location).samefile(pkg_path.dirname()):
        dist = None
    assert zetup.__distribution__ == zfg.DISTRIBUTION.find(pkg_path) \
      == dist

    assert zetup.__version__ == zfg.VERSION
    if in_site_packages:
        assert zetup.__version__ == (zfg_path / 'VERSION').text().strip()

    assert str(zetup.__requires__) == str(zfg.REQUIRES)
           ## == (path / 'requirements.txt').text())
