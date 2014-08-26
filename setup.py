from zetup import Zetup


zetup = Zetup()
zetup(
  setup_requires=['hgdistver'],

  get_version_from_scm=True,

  entry_points={'distutils.setup_keywords': [
    'use_zetup = zetup:setup_entry_point',
    ]},

  scripts=['scripts/zetup'],
  )
