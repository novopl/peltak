# pylint: disable=missing-docstring
import pytest

from peltak.core.templates.filters import count_flag_filter


@pytest.mark.parametrize('count,flag,expected_value', [
    (0, 'v', ''),
    (1, 'v', '-v'),
    (2, 'v', '-vv'),
    (3, 'e', '-eee'),
    (4, 'y', '-yyyy'),
])
def test_works(count, flag, expected_value):
    result = count_flag_filter(count, flag)

    assert result == expected_value


@pytest.mark.parametrize('count', [-1, -2, -10, 'a', None])
def test_raises_ValueError_on_invalid_count(count):
    with pytest.raises(ValueError):
        count_flag_filter(count, 'v')


@pytest.mark.parametrize('flag', ['vv', '9', '-', '+', '*', 3, 12, None])
def test_raises_ValueError_if_flag_is_invalid(flag):
    with pytest.raises(ValueError):
        count_flag_filter(2, flag)
