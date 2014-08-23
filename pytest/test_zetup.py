from pkg_resources import get_distribution

from path import path as Path

import zetup


def test_zetup():
    from zetup import zetup as z

    path = Path(z.ZETUP_DIR)

    assert(z.NAME == 'zetup')

    ## assert(zetup.__distribution__ == z.DISTRIBUTION.find(zetup.__path__[0])
    ##        == get_distribution('zetup'))

    assert(zetup.__version__ == z.VERSION
           == (path / 'VERSION').text().strip())

    ## assert(str(zetup.__requires__) == str(z.REQUIRES)
    ##        == (path / 'requirements.txt').text())
