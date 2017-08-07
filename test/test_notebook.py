"""Test the zetup.notebook.Notebook class.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from inspect import getmembers

import nbconvert

import pytest


class TestNotebook(object):
    """Test zetup.Notebook features using zetup's own README notebook.
    """
    def test_converters(self, notebook, in_site_packages):
        if in_site_packages:
            # notebooks aren't installed
            assert notebook is None
            return
        # check if all nbconvert exporters are exposed to the notebook
        # instance as to_...() methods
        for name in nbconvert.get_export_names():
            converter = getattr(notebook, 'to_' + name)
            assert callable(converter)
        # and if the conversion actually works by testing with markdown export
        assert nbconvert.MarkdownExporter().from_filename(notebook)[0] \
            == notebook.to_markdown()

    def test_getattr(self, notebook, in_site_packages):
        if in_site_packages:
            # notebooks aren't installed
            assert notebook is None
            return
        # check correct AttributeError messages
        # (if a non-existing attribute starts with 'to_',
        #  __getattr__ should report that such a 'converter'
        #  instead of 'attribute' does not exist)
        with pytest.raises(AttributeError) as exc:
            notebook.not_defined
        assert all(text in str(exc.value) for text in [
          "has no attribute", "not_defined"])
        assert "converter" not in str(exc.value)
        with pytest.raises(AttributeError) as exc:
            notebook.to_not_defined()
        assert all(text in str(exc.value) for text in [
          "has no converter", "to_not_defined"])
