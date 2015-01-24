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

__all__ = ['Notebook']

import re
from inspect import getmembers

try:
    from path import Path as base
except ImportError:
    base = str


class Notebook(base):

    def __dir__(self):
        """Return names of dynamically generatable .to_...() converter methods
           with IPython.nbconvert.export_...() delegation.
        """
        # import on demand to be not required for module import
        from IPython import nbconvert
        return ['to_' + name.split('_', 1)[1]
                for name, member in getmembers(nbconvert)
                if name.startswith('export_')]

    def __getattr__(self, name):
        """Dynamically generate .to_...() converter methods
           with IPython.nbconvert.export_...() delegation.
        """
        if not name.startswith('to_'):
            raise AttributeError(
              "%s instance has no attribute %s" % (type(self), repr(name)))

        # import on demand to be not required for module import
        from IPython import nbconvert
        func = getattr(nbconvert, 'export_' + name.split('_', 1)[1])

        def method():
            return func(self)

        method.__name__ = name
        return method

    def to_bitbucket_rst(self):
        """Export the notebook to Bitbucket optimized reST.

        - Prepends 'rst-header-' to link targets.
          ('#some-section' --> '#rst-header-some-section')
        """
        # import on demand to be not required for module import
        from IPython import nbconvert
        from .jinja import FILTERS, LOADER

        rst = nbconvert.export_rst(self,
          filters=FILTERS, extra_loaders=[LOADER],
          # Not a real file,
          #  will be loaded from string by LOADER:
          template_file='bitbucket_rst',
          )[0]
        # bitbucket_rst template puts code cell input and output
        #  in single blocks, but can't prevent empty lines in between
        #==> Remove them:
        return re.sub(
          # .. code:: python
          #
          #     >>> input
          #
          #     output
          r'(\n    >>> .+\n)\s*\n(    [^>])',
          # .. code:: python
          #
          #     >>> input
          #     output
          r'\1\2',
          rst)

    def to_github_markdown(self):
        """Export the notebook to Github optimized Markdown.

        - Removes header enumeration prefixes from link targets.
          ('#1.-section-one' --> '#section-one')
        """
        # import on demand to be not required for module import
        from IPython import nbconvert
        from .jinja import FILTERS, LOADER

        markdown = nbconvert.export_markdown(self,
          filters=FILTERS, extra_loaders=[LOADER],
          # Not a real file,
          #  will be loaded from string by LOADER:
          template_file='github_markdown',
          )[0]
        # github_markdown template puts code cell input and output
        #  in single blocks, but can't prevent empty lines in between
        #==> Remove them:
        markdown = re.sub(
          # ```python
          # >>> input
          #
          # output
          # ```
          r'(\n>>> .+\n)\s*\n([^>`])',
          # ```python
          # >>> input
          # output
          # ```
          r'\1\2',
          markdown)
        # And also remove newlines after ```python and before ```:
        markdown = re.sub(r'(\n```python.*\n)\s*', r'\1', markdown)
        markdown = re.sub(r'\n\s*(```\s*\n)', r'\n\1', markdown)
        return markdown
