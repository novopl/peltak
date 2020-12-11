# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak import testing
from peltak.core import versioning


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.current')
@patch('peltak.core.versioning.write')
def test_uses_current_and_write_for_actual_operation(p_write, p_current):
    p_current.return_value = '0.9.5'

    versioning.bump()

    p_current.assert_called_once_with()
    p_write.assert_called_once_with('0.9.6')


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.get_version_storage', Mock())
def test_raises_ValueError_if_invalid_version_is_given():
    with pytest.raises(ValueError):
        versioning.bump(exact='invalid_ver')


@pytest.mark.parametrize('version,component,expected', [
    ('0.9.5', 'patch', '0.9.6'),
    ('0.9.5', 'minor', '0.10.0'),
    ('0.9.5', 'major', '1.0.0'),
    ('0.9.0', 'patch', '0.9.1'),
])
@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.current')
@patch('peltak.core.versioning.write')
def test_properly_bumps_the_version(p_write,
                                    p_current,
                                    version,
                                    component,
                                    expected):
    p_current.return_value = version

    versioning.bump(component)

    p_current.assert_called_once_with()
    p_write.assert_called_once_with(expected)


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.current')
@patch('peltak.core.versioning.write', Mock())
def test_raises_ValueError_if_current_version_is_invalid(p_current):
    p_current.return_value = 'invalid_ver'

    with pytest.raises(ValueError):
        versioning.bump()


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.current', Mock(return_value='0.9.5'))
@patch('peltak.core.versioning.write', Mock())
def test_raises_ValueError_if_invalid_component_is_passed():
    with pytest.raises(ValueError):
        versioning.bump('invalid_component')
