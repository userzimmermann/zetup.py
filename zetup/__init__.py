COMMANDS = ['init']

__all__ = ['COMMANDS'] + COMMANDS

# Import zetup script to get zetup's own setup data:
from . import zetup


# z = zetup.Zetup()

# ## __distribution__ = zetup.DISTRIBUTION.find(__path__[0])
# __description__ = z.DESCRIPTION

# __version__ = z.VERSION

# __requires__ = z.REQUIRES.checked
# __extras__ = z.EXTRAS

# __notebook__ = z.NOTEBOOKS['README']

import os
from subprocess import call

from path import path as Path

from .zetup import Zetup


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
