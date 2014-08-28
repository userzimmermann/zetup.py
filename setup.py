from zetup import Zetup
try:
    import zetup.commands
except ImportError:
    pass


zetup = Zetup()

package_data = zetup.setup_keywords()['package_data']
package_data['zetup.commands.make'] = ['templates/*.jinja']

zetup(
  setup_requires=['hgdistver'],

  get_version_from_scm=True,

  entry_points={'distutils.setup_keywords': [
    'use_zetup = zetup:setup_entry_point',
    ]},

  package_data=package_data,

  scripts=['scripts/zetup'],
  )
