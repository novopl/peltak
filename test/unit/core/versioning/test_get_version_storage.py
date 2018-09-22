# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import Mock, patch

# 3rd party imports
import pytest

# local imports
from peltak import testing
from peltak.core import versioning


@testing.patch_pelconf({'version_file': 'fake.py'})
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_returns_PyVersionStorage_if_file_ends_with_py():
    storage = versioning.get_version_storage()

    assert isinstance(storage, versioning.PyVersionStorage)


@testing.patch_pelconf({'version_file': 'package.json'})
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_returns_NodeVersionStorage_if_file_name_is_package_json():
    storage = versioning.get_version_storage()

    assert isinstance(storage, versioning.NodeVersionStorage)


@pytest.mark.parametrize('version_file', [
    'VERSION',
    'version.txt',
    'any_file.json',
    'fake.py.txt',
])
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_returns_NodeVersionStorage_if_nothing_else_is_recognized(version_file):
    with testing.patch_pelconf({'version_file': version_file}):
        storage = versioning.get_version_storage()

    assert isinstance(storage, versioning.RawVersionStorage)
