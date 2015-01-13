from textwrap import dedent
from warnings import warn

from zetup import Zetup
try: # needs zetup's requirements to be installed
    import zetup.commands
except Exception as e:
    warn(dedent("""
      Can't load all zetup features.
      You should install requirements from 'requirements.commands.txt'
      (ImportError: %s)
      """ % e).strip())


zetup = Zetup()

setup = zetup.setup
setup['package_data']['zetup.commands.make'] = [
  'templates/*.jinja',
  'templates/package/*.jinja',
  ]
setup(
  ## setup_requires=['hgdistver >= 0.23'],

  ## get_version_from_scm=True,

  entry_points={'distutils.setup_keywords': [
    'use_zetup = zetup:setup_entry_point',
    ]},

  scripts=['scripts/zetup'],
  )
