# pylint: disable=missing-docstring
import pytest

from peltak.core import fs


def test_works_as_expected():
    paths = ['one.txt', 'two.txt', 'three/path', 'hello world']
    result = fs.wrap_paths(paths)

    assert result == '"one.txt" "two.txt" "three/path" "hello world"'


def test_raises_ValueError_if_given_a_string_as_argument():
    with pytest.raises(ValueError):
        fs.wrap_paths('string')
