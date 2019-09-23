# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest


# local imports
from peltak.extra.scripts.logic import ScriptOption


@pytest.fixture()
def opt_conf():
    def make_conf(**values):
        defaults = {
            'about': 'Test option help',
            'is_flag': True,
            'default': False,
        }
        defaults.update(values)
        return defaults

    yield make_conf


def test_works(opt_conf):
    opt = ScriptOption.from_config(opt_conf(
        name=['-f', '--force'],
        about='Force the execution, will not ask any questions',
        is_flag=True,
        default=False,
    ))

    assert opt.name == ['-f', '--force']
    assert opt.about == 'Force the execution, will not ask any questions'
    assert opt.default is False
    assert opt.is_flag is True


def test_raises_ValueError_if_name_is_not_defined(opt_conf):
    with pytest.raises(ValueError):
        ScriptOption.from_config(opt_conf())


@pytest.mark.parametrize('name', (None, [], ''))
def test_raises_ValueError_if_name_is_empty(name, opt_conf):
    with pytest.raises(ValueError):
        ScriptOption.from_config(opt_conf(name=name))


def test_supports_passing_the_name_as_string(opt_conf):
    opt = ScriptOption.from_config(opt_conf(name='--force'))

    assert opt.name == ['--force']
