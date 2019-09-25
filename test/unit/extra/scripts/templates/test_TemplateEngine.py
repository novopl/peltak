# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest
from mock import Mock, patch

# local imports
from peltak.core import util
from peltak.extra.scripts.templates import TemplateEngine


def test_is_singleton():
    assert TemplateEngine() is TemplateEngine()


@patch.object(TemplateEngine, '_make_env')
def test_calls_make_env_when_created_for_the_first_time(p_make_env):
    # type: (Mock) -> None
    # Make sure we don't have any lingering instance from other tests.
    util.Singleton.instances = {}

    TemplateEngine()

    p_make_env.assert_called_once()

    # Clean-up afterwards (TemplateEngine is a singleton so changes will be
    # preserved after the test finishes - TemplateEngine.env is a Mock).
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
    assert filter_name in TemplateEngine().env.filters


def test_uses_double_curly_brace_for_expressions():
    assert TemplateEngine().env.variable_start_string == '{{'
    assert TemplateEngine().env.variable_end_string == '}}'
