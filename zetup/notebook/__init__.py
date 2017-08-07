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

# TODO: not working because module is imported
# before main zetup module is annotated
#
# import zetup
#
# __requires__ = zetup.__requires__ + zetup.__extras__['notebook']

import re
from inspect import getmembers

try:
    #TODO: zetup.Path base
    from path import Path as base
except ImportError:
    # just reduce features
    base = str

from zetup.object import object


def check_requirements(raise_=True):
    """Check requirements for full :class:`zetup.Notebook` features.
    """
    import zetup
    return zetup.__extras__['notebook'].check(raise_=raise_)


class Notebook(object, base):

    def __dir__(self):
        """Return names of dynamically generatable
           ``.to_...()`` converter methods
           with ``nbconvert.export_...()`` delegation.
        """
        if not check_requirements(raise_=False):
            return []
        # import on demand to be not required for module import
        import nbconvert
        return super(Notebook, self).__dir__() + [
            'to_' + name for name in nbconvert.get_export_names()]

    def __getattr__(self, name):
        """Dynamically generate ``.to_...()`` converter methods
           with ``nbconvert.export_...()`` delegation.
        """
        if not name.startswith('to_'):
            raise AttributeError(
              "%s instance has no attribute %s" % (type(self), repr(name)))

        check_requirements()
        # import on demand to be not required for module import
        import nbconvert
        try:
            exportercls = nbconvert.get_exporter(name.split('_', 1)[1])
        except ValueError as e:
            raise AttributeError(
              "%s instance has no converter method %s (%s: %s)"
              % (type(self), repr(name), type(e).__name__, e))

        def method():
            result = exportercls().from_filename(self)
            return result[0] # only the actual text

        method.__name__ = name
        return method

    def to_bitbucket_rst(self):
        """Export the notebook to Bitbucket optimized reST.

        - Prepends 'rst-header-' to link targets.
          ('#some-section' --> '#rst-header-some-section')
        """
        check_requirements()
        # import on demand to be not required for module import
        import nbconvert
        from .jinja import FILTERS, LOADER

        exporter = nbconvert.RSTExporter()
        exporter.filters = FILTERS
        exporter.extra_loaders = [LOADER]
        # not a real file. will be loaded from string by LOADER
        exporter.template_file = 'bitbucket_rst'
        rst = exporter.from_filename(self)[0]
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
        check_requirements()
        # import on demand to be not required for module import
        import nbconvert
        from .jinja import FILTERS, LOADER

        exporter = nbconvert.MarkdownExporter()
        exporter.filters = FILTERS
        exporter.extra_loaders = [LOADER]
        # not a real file. will be loaded from string by LOADER
        exporter.template_file = 'github_markdown'
        markdown = exporter.from_filename(self)[0]
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
