from textwrap import dedent
from warnings import warn

from zetup import Zetup
try: # needs zetup's requirements to be installed
    import zetup.commands
except ImportError as e:
    raise RuntimeError(dedent("""
      Can't load all zetup features.
      You should install zetup's requirements from 'requirements.txt'.
      (ImportError: %s)
      """ % e).strip())


zetup = Zetup()

setup = zetup.setup
setup['package_data']['zetup.commands.make'] = ['templates/*.jinja']
setup(
  setup_requires=['hgdistver'],

  get_version_from_scm=True,

  entry_points={'distutils.setup_keywords': [
    'use_zetup = zetup:setup_entry_point',
    ]},

  scripts=['scripts/zetup'],
  )
