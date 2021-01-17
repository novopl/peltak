# pylint: disable=missing-docstring
import pytest

from peltak.core import versioning


def test_raises_ValueError_if_invalid_version_is_given(app_conf):
    with pytest.raises(ValueError):
        versioning.write('invalid')
