# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak.core import versioning


class FakeStorage(versioning.VersionStorage):
    pass


@patch('peltak.core.versioning.exists', Mock(return_value=False))
def test_raises_ValueError_if_version_file_does_not_exist():

    with pytest.raises(ValueError):
        FakeStorage('fake_version_file')


@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_raises_NotImplementedError_if_read_is_not_implemented():
    storage = FakeStorage('fake_version_file')

    with pytest.raises(NotImplementedError):
        storage.read()


@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_raises_NotImplementedError_if_write_is_not_implemented():
    storage = FakeStorage('fake_version_file')

    with pytest.raises(NotImplementedError):
        storage.write('0.0.0')
