# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import os
from subprocess import call

from zetup import Zetup


@Zetup.command(depends=['VERSION', 'setup.py', '__init__.py'])
def conda(self, args):
    """The actual conda command action called by Command base.
    """
    from path import path as Path
    import yaml

    metadir = Path('.conda')
    metadir.mkdir_p()
    metafile = metadir / 'meta.yaml'
    buildfile = metadir / 'build.sh'

    def conda_req(req):
        """conda wants space between requirement name and version specs.
        """
        return re.sub(r'([=<>]+)', r' \1', str(req))

    requirements = list(map(conda_req, self.REQUIRES))
    # Also add all extra requirements
    #  (conda doesn't seem to have such an extra features management):
    for extra in self.EXTRAS.values():
        requirements.extend(map(conda_req, extra))

    meta = { # to be dumped to meta.yaml
      'package': {
        'name': self.NAME,
        'version': str(self.VERSION),
        },
      'source': {
        'fn': '%s-%s.tar.gz' % (self.NAME, self.VERSION),
        # The absolute path to the sdist in dist/
        'url': 'file://%s' % os.path.realpath(os.path.join(
          'dist', '%s-%s.tar.gz' % (self.NAME, self.VERSION)))
        },
      'requirements': {
        'build': [
          'python',
          'pyyaml',
          ] + requirements,
        'run': [
          'python',
          ] + requirements,
        },
      'about': {
        'home': self.URL,
        'summary': self.DESCRIPTION,
        },
      }
    with open(metafile, 'w') as f:
        yaml.dump(meta, f, default_flow_style=False)

    with open(buildfile, 'w') as f:
        f.write('#!/bin/bash'
                '\n\n'
                '$PYTHON setup.py install'
                '\n')

    status = call(['conda', 'build', metadir])
    if not status:
        sys.exit(status)
