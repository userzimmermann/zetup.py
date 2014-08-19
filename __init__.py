COMMANDS = ['init']

__all__ = ['COMMANDS'] + COMMANDS

from . import zetup

__distribution__ = zetup.DISTRIBUTION.find(__path__[0])
__description__ = zetup.DESCRIPTION

__version__ = zetup.VERSION

__requires__ = zetup.REQUIRES.checked
__extras__ = zetup.EXTRAS

__notebook__ = zetup.NOTEBOOKS['README']

import os

from path import path as Path


def init(name, path=None):
    path = Path(path or os.getcwd())
    Path(__path__[0] / 'zetup.py').copy(path / '__init__.py')
    with open(path / 'zetuprc', 'w') as f:
        f.write("[%s]\n\n%s\n" % (name, "\n".join("%s =" % key for key in [
          'description',
          'author',
          'url',
          'license',
          'python',
          'classifiers',
          'keywords',
          ])))
    with open(path / 'VERSION', 'w') as f:
        f.write("0.0.0\n")
