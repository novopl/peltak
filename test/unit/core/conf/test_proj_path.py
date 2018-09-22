# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest
from mock import patch

# local imports
from peltak import testing
from peltak.core import conf


@pytest.mark.parametrize('proj_path,abs_path', [
    ('testfile', '/fake/proj/testfile'),
    ('sub/testfile', '/fake/proj/sub/testfile'),
    ('/abs/path', '/abs/path'),
])
@patch('peltak.core.conf.g_proj_path', '/fake/proj')
def test_converts_project_path_to_an_absolute_path(proj_path, abs_path):
    assert conf.proj_path(proj_path) == abs_path


@testing.patch_proj_root(None)
def test_returns_input_path_if_no_project_root_found():
    assert conf.proj_path('hello/world') == 'hello/world'
