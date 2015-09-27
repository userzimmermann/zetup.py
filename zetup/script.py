#!python

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

from __future__ import absolute_import, print_function

import sys
from itertools import chain
from argparse import ArgumentParser
import distutils.command

import zetup.commands
from zetup.commands import ZetupCommandError, make, pytest, tox, conda
from zetup.process import call


EXTERNAL_COMMANDS = []

COMMANDS = sorted(chain(
  distutils.command.__all__,
  zetup.commands.COMMANDS,
  zetup.Zetup.COMMANDS,
  EXTERNAL_COMMANDS,
  ))

ap = ArgumentParser()
ap.add_argument(
  'cmd', choices=COMMANDS,
  help="command",
  )

args = ap.parse_args()


def run():
    exit_status = 0 # exit status of this script
    try:
        cmdfunc = zetup.commands.COMMANDS[args.cmd]
    except KeyError:
        if args.cmd in EXTERNAL_COMMANDS:
            exit_status = call([args.cmd])
        else:
            zfg = zetup.Zetup()
            if args.cmd in zfg.COMMANDS:
                try:
                    exit_status = getattr(zfg, args.cmd)()
                except ZetupCommandError as e:
                    print("Error: %s" % e, file=sys.stderr)
                    exit_status = 1
                else:
                    try: # return value can be more than just a status number
                        exit_status = exit_status.status
                    except AttributeError:
                        pass
            else: # ==> standard setup command
                zfg(subprocess=True)
    else:
        exit_status = cmdfunc()

    sys.exit(exit_status or 0)


if __name__ == '__main__':
    run()
