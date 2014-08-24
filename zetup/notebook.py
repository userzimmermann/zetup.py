# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

__all__ = ['Notebook']

import re


try:
    from path import path as Path
except ImportError:
    class Notebook(str):
        pass
else:
    try:
        from IPython import nbconvert
        from jinja2 import BaseLoader, TemplateNotFound
    except ImportError:
        class Notebook(Path):
            pass
    else:
        from inspect import getmembers
        from textwrap import dedent


        def bitbucket_rst_links(rst):
            return re.sub(
              r'<#[0-9.-]+([^>]+)>',
              lambda match: '<#rst-header-%s>' % match.group(1).lower(),
              rst)


        def github_markdown_links(markdown):
            return re.sub(
              r'\[([^\]]+)\]: #(.+)',
              lambda match: '[%s]: #%s' % (
                match.group(1), match.group(2).replace('.', '').lower()),
                markdown)


        class ExtraTemplateLoader(BaseLoader):
            templates = {
              'bitbucket_rst': dedent("""
                {%- extends 'rst.tpl' -%}


                {% block input %}
                {%- if cell.input.strip() -%}

                .. code:: python

                {% if cell.outputs %}
                {{ cell.input | add_prompts(cont='>>> ') | indent }}
                {% else %}
                {{ cell.input | indent }}
                {% endif %}
                {%- endif -%}
                {% endblock input %}


                {% block stream %}
                {{ output.text | indent }}
                {% endblock stream %}


                {% block data_text scoped %}
                {{ output.text | indent }}
                {% endblock data_text %}


                {% block markdowncell scoped %}
                {{ super() | bitbucket_rst_links }}
                {% endblock markdowncell %}
                """),

              'github_markdown': dedent("""
                {%- extends 'markdown.tpl' -%}


                {% block input %}
                ```python
                {% if cell.outputs %}
                {{ cell.input | add_prompts(cont='>>> ') }}
                {% else %}
                {{ cell.input }}
                ```
                {% endif %}
                {% endblock input %}


                {% block stream %}
                {{ output.text }}
                ```
                {% endblock stream %}


                {% block data_text scoped %}
                {{ output.text }}
                ```
                {% endblock data_text %}


                {% block markdowncell scoped %}
                {{ super() | github_markdown_links }}
                {% endblock markdowncell %}
                """),
              }

            def get_source(self, env, template):
                try:
                    return self.templates[template], template, True
                except KeyError:
                    raise TemplateNotFound(template)


        class Notebook(Path):
            EXTRA_FILTERS = {
              'bitbucket_rst_links': bitbucket_rst_links,
              'github_markdown_links': github_markdown_links,
              }

            EXTRA_LOADER = ExtraTemplateLoader()

            def to_bitbucket_rst(self):
                """Export the notebook to Bitbucket optimized reST.

                - Prepends 'rst-header-' to link targets.
                  ('#some-section' --> '#rst-header-some-section')
                """
                rst = nbconvert.export_rst(self,
                  filters=self.EXTRA_FILTERS,
                  extra_loaders=[self.EXTRA_LOADER],
                  # Not a real file,
                  #  will be loaded from string by EXTRA_LOADER:
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
                markdown = nbconvert.export_markdown(self,
                  filters=self.EXTRA_FILTERS,
                  extra_loaders=[self.EXTRA_LOADER],
                  # Not a real file,
                  #  will be loaded from string by EXTRA_LOADER:
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


        def _exportmethod(name, func):
            def method(self):
                return func(self)

            method.__name__ = 'to_' + name
            return method


        for name, member in getmembers(nbconvert):
            if name.startswith('export_'):
                name = name.split('_', 1)[1]
                if name != 'by_name':
                    setattr(Notebook, 'to_' + name,
                            _exportmethod(name, member))
