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

from pkg_resources import get_distribution

from zetup.process import call
from zetup.zetup import ZetupConfigNotFound
from zetup.commands import ZetupCommandError
import zetup.commands


EXTERNAL_COMMANDS = []

COMMANDS = sorted(chain(
    distutils.command.__all__,
    zetup.commands, zetup.Zetup.COMMANDS,
    EXTERNAL_COMMANDS,
))

PARSER = ArgumentParser()
PARSER.add_argument(
    'cmd', choices=COMMANDS,
    help="command",
)


def run(argv=None, cmd=None):
    """Run the **zetup** script.

    - If no `argv` is given, arguments are taken from ``sys.argv``.
    - Optionally takes an explicit zetup `cmd` not contained in `argv`.
    """
    print(repr(get_distribution('zetup')))

    argv = sys.argv[1:] if argv is None else list(argv)
    if cmd:
        argv.insert(1, str(cmd))
    args = PARSER.parse_args(argv)

    exit_status = 0 # exit status of this script
    try:
        zfg = zetup.Zetup()
    except ZetupConfigNotFound as no_zfg:
        try:
            cmdfunc = zetup.commands[args.cmd]
        except KeyError:
            raise no_zfg
    else:
        if args.cmd in zfg.COMMANDS:
            cmdfunc = getattr(zfg, args.cmd)
        else: # ==> standard setup command
            sys.exit(zfg(subprocess=True))

    try:
        exit_status = cmdfunc()
    except ZetupCommandError as exc:
        print("Error: %s" % exc, file=sys.stderr)
        exit_status = 1
    else:
        try: # return value can be more than just a status number
            exit_status = exit_status.status
        except AttributeError:
            pass

    sys.exit(exit_status or 0)


if __name__ == '__main__':
    run()
