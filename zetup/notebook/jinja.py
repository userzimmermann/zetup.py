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

__all__ = ['FILTERS', 'LOADER']

import re
from textwrap import dedent

from jinja2 import BaseLoader, TemplateNotFound


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


FILTERS = {
  'bitbucket_rst_links': bitbucket_rst_links,
  'github_markdown_links': github_markdown_links,
  }


class ExtraTemplateLoader(BaseLoader):
    templates = {
      'bitbucket_rst': dedent("""
        {%- extends 'rst.tpl' -%}


        {% block input %}
        {%- if cell.source.strip() -%}

        .. code:: python

        {% if cell.outputs %}
        {{ cell.source | add_prompts(cont='>>> ') | indent }}
        {% else %}
        {{ cell.source | indent }}
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
        {{ cell.source | add_prompts(cont='>>> ') }}
        {% else %}
        {{ cell.source }}
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


LOADER = ExtraTemplateLoader()
