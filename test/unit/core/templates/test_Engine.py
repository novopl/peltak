# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak.core import util
from peltak.core import templates


def test_is_singleton():
    assert templates.Engine() is templates.Engine()


@patch.object(templates.Engine, '_make_env')
def test_calls_make_env_when_created_for_the_first_time(p_make_env):
    # type: (Mock) -> None
    # Make sure we don't have any lingering instance from other tests.
    util.Singleton.instances = {}

    templates.Engine()

    p_make_env.assert_called_once()

    # Clean-up afterwards (Engine is a singleton so changes will be
    # preserved after the test finishes - Engine.env is a Mock).
    util.Singleton.instances = {}


@pytest.mark.parametrize('filter_name', [
    'header',
    'count_flag',
    'cprint',
    'wrap_paths',
])
def test_has_all_filters(filter_name):
    # type: (str) -> None
    # Make sure we don't have any lingering instance from other tests.
    assert filter_name in templates.Engine().env.filters


def test_uses_double_curly_brace_for_expressions():
    assert templates.Engine().env.variable_start_string == '{{'
    assert templates.Engine().env.variable_end_string == '}}'


# Used only in type hint comments
del Mock
