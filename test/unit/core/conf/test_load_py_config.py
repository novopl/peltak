# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# 3rd party imports
import pytest
from mock import patch

# local imports
from peltak.core import conf


@pytest.mark.skipif(sys.version_info < (3, 5), reason="Only run on py35+")
@patch('importlib.util.spec_from_file_location')
@patch('importlib.util.module_from_spec')
@patch('sys.version_info', (3, 5))
def test_uses_importlib_util_on_py35_plus(p_module_from_spec,
                                          p_spec_from_file_location):
    conf.load_py_config('fake.py')

    p_module_from_spec.assert_called()
    p_spec_from_file_location.assert_called()


@pytest.mark.skipif(sys.version_info < (3, 3), reason="Only run on py33")
@patch('importlib.machinery.SourceFileLoader')
@patch('sys.version_info', (3, 3))
def test_uses_importlib_machinery_on_py33(p_source_file_loader):
    conf.load_py_config('fake.py')

    p_source_file_loader.assert_called()


@pytest.mark.skipif(sys.version_info < (3, 4), reason="Only run on py34")
@patch('importlib.machinery.SourceFileLoader')
@patch('sys.version_info', (3, 4))
def test_uses_importlib_machinery_on_py34(p_source_file_loader):
    conf.load_py_config('fake.py')

    p_source_file_loader.assert_called()


@patch('imp.load_source')
@patch('sys.version_info', (2, 7))
def test_uses_imp_on_py27(p_load_source):
    conf.load_py_config('fake.py')

    p_load_source.assert_called()
