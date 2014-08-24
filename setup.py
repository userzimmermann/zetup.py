exec(open('zetup.py').read())


zetup = Zetup()
zetup(
  package_dir={'zetup': '.'},
  packages=['zetup'],
  package_data={'zetup': zetup.ZETUP_DATA},

  scripts=['scripts/zetup'],
  )
