# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak.core import versioning


@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_returns_PyVersionFile_if_file_ends_with_py(app_conf):
    version_file = versioning.load_version_file('fake.py')

    assert isinstance(version_file, versioning.PyVersionFile)


@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_returns_NodeVersionFile_if_file_name_is_package_json(app_conf):
    version_file = versioning.load_version_file('package.json')

    assert isinstance(version_file, versioning.NodeVersionFile)


@pytest.mark.parametrize('version_file', [
    'VERSION',
    'version.txt',
    'any_file.json',
    'fake.py.txt',
])
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_returns_RawVersionFile_if_nothing_else_is_recognized(app_conf, version_file):
    version_file = versioning.load_version_file(version_file)

    assert isinstance(version_file, versioning.RawVersionFile)
