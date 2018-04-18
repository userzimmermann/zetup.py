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


def smart_prompts(source, prompt='>>> ', cont='... '):
    return '\n'.join(
        (not re.match(r'^\s', line) and prompt or cont) + line
        for line in source.split('\n'))


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
    'smart_prompts': smart_prompts,
    'bitbucket_rst_links': bitbucket_rst_links,
    'github_markdown_links': github_markdown_links,
}


class ExtraTemplateLoader(BaseLoader):
    templates = {
      'bitbucket_rst': dedent("""
        {%- extends 'rst.tpl' -%}

        {% block input %}
        {% if cell.source.strip() -%}
        {% if not cell.source.startswith(('%', '!')) -%}
        .. code:: python
        {%- else -%}
        {% if cell.source.startswith('%%file') -%}
        .. code:: {{ cell.source.split('\\n')[0].rsplit('.', 1)[1] }}
        {%- else -%}
        .. code::
        {%- endif %}
        {%- endif %}

        {% if cell.outputs and not cell.source.startswith(('%', '!')) -%}
        {{ cell.source | smart_prompts | indent }}
        {%- else -%}
        {{ cell.source | smart_prompts | indent }}
        {%- endif %}
        {%- endif %}
        {% endblock input %}

        {% block stream -%}
        .. code::

        {{ output.text | indent }}
        {%- endblock stream %}

        {% block data_text scoped -%}
        {{ output.data['text/plain'] | indent }}
        {%- endblock data_text %}

        {% block markdowncell scoped %}
        {{ super() | bitbucket_rst_links }}
        {% endblock markdowncell %}
        """),

      'github_markdown': dedent("""
        {%- extends 'markdown.tpl' -%}

        {% block input %}
        {% if cell.source.strip() %}
        {% if not cell.source.startswith(('%', '!')) -%}
        ```python
        {%- else -%}
        {% if cell.source.startswith('%%file') -%}
        ```{{ cell.source.split('\\n')[0].rsplit('.', 1)[1] }}
        {%- else -%}
        ```
        {%- endif %}
        {%- endif %}
        {% if cell.outputs and not cell.source.startswith(('%', '!')) -%}
        {{ cell.source | smart_prompts }}
        {%- else -%}
        {{ cell.source | smart_prompts }}
        {% if not cell.outputs -%}
        ```
        {%- endif %}
        {%- endif %}
        {%- endif %}
        {% endblock input %}

        {% block stream -%}
        ```

        ```
        {{ output.text }}
        ```
        {%- endblock stream %}

        {% block data_text scoped -%}
        {{ output.data['text/plain'] }}
        ```
        {%- endblock data_text %}

        {% block markdowncell scoped %}
        {{ super() | github_markdown_links }}
        {% endblock markdowncell %}
        """),
      }

    def get_source(self, env, template):
        if template not in self.templates:
            raise TemplateNotFound(template)
        # must return (template text, template name, up_to_date() function)
        return self.templates[template], template, lambda: True


LOADER = ExtraTemplateLoader()
