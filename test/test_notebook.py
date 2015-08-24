"""Test the zetup.notebook.Notebook class.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from inspect import getmembers

import nbconvert

import pytest


def test_zetup_notebook(zfg, in_site_packages):
    """Test zetup.Notebook features using zetup's own README notebook.
    """
    if in_site_packages:
        # notebooks aren't installed
        return

    notebook = zfg.NOTEBOOKS['README']

    #--- CONVERTERS ---

    # check if all IPython.nbconvert.export_...() converters
    # are exposed to the notebook instance as to_...() methods
    for name, obj in getmembers(nbconvert):
        if name.startswith('export_'):
            converter = getattr(notebook, 'to_' + name.split('_', 1)[1])
            assert callable(converter)

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
