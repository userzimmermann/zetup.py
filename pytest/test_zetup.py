from inspect import ismodule

from pkg_resources import get_distribution

from path import path as Path

import zetup
from zetup import Zetup, find_zetup_config


def test_zetup():
    zfg = find_zetup_config('zetup')

    pkg_path = Path(zetup.__path__[0]).realpath()
    zfg_path = Path(zfg.ZETUP_DIR).realpath()

    assert ismodule(zfg) and zfg_path == (pkg_path / 'zetup_config') \
      or isinstance(zfg, Zetup) and zfg_path == pkg_path.dirname()

    assert(zfg.NAME == 'zetup')

    dist = get_distribution('zetup')
    if Path(dist.location).realpath() != pkg_path.dirname():
        dist = None
    assert zetup.__distribution__ == zfg.DISTRIBUTION.find(pkg_path) \
      == dist

    assert(zetup.__description__ == zfg.DESCRIPTION)

    assert(zetup.__version__ == zfg.VERSION
           == (zfg_path / 'VERSION').text().strip())

    assert(str(zetup.__requires__) == str(zfg.REQUIRES))
           ## == (path / 'requirements.txt').text())
