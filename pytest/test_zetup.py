from pkg_resources import get_distribution

from path import path as Path

import zetup


def test_zetup():
    from zetup.zetup import NAME, DISTRIBUTION, VERSION, REQUIRES

    path = Path(zetup.__path__[0])

    assert(NAME == 'zetup')

    assert(zetup.__distribution__ == DISTRIBUTION.find(zetup.__path__[0])
           == get_distribution('zetup'))

    assert(zetup.__version__ == VERSION
           == (path / 'VERSION').text().strip())

    ## assert(str(zetup.__requires__) == str(REQUIRES)
    ##        == (path / 'requirements.txt').text())
