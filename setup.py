exec(open('zetup.py').read())


zetup(
  package_dir={'zetup': ZETUP_DIR},
  packages=['zetup'],
  package_data={'zetup': ZETUP_DATA},

  scripts=['scripts/zetup'],
  )
