exec(open('zetup.py').read())


zetup(
  package_dir={'zetup': '.'},
  packages=['zetup'],
  package_data={'zetup': ZETUP_DATA},

  scripts=['scripts/zetup'],
  )
