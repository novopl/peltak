# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest


# local imports
from peltak.core import types
from peltak.extra.scripts.types import Script, ScriptOption


def test_works():
    script = Script.from_config('test', {
        'about': 'Test script',
        'command': 'echo test',
        'success_exit_codes': [0, 5],
        'root_cli': True,
        'files': {
            'paths': ['src'],
        },
        'options': [
            {
                'name': ['-f', '--force'],
                'about': 'Force something',
                'is_flag': True,
            }
        ],
    })

    assert script.name == 'test'
    assert script.about == 'Test script'
    assert script.root_cli is True
    assert script.success_exit_codes == [0, 5]
    assert script.command == 'echo test'

    assert isinstance(script.files, types.FilesCollection)
    assert script.files.paths == ['src']

    assert isinstance(script.options, list)
    assert len(script.options) == 1
    assert isinstance(script.options[0], ScriptOption)
    assert script.options[0].name == ['-f', '--force']
    assert script.options[0].about == "Force something"
    assert script.options[0].is_flag is True
    assert script.options[0].default is None


def test_works_with_just_name_and_command():
    script = Script.from_config('test', {
        'command': 'echo test'
    })

    assert script
    assert script.name == 'test'
    assert script.command == 'echo test'
    assert script.about == ''
    assert script.files is None
    assert script.success_exit_codes == [0]


def test_raises_ValueError_if_command_is_not_defined():
    with pytest.raises(ValueError):
        Script.from_config('test', {})


def test_supports_passing_scalar_to_success_exit_codes():
    script = Script.from_config('test', {
        'command': 'fake_cmd',
        'success_exit_codes': 5,
    })

    assert script.name == 'test'
    assert script.command == 'fake_cmd'
    assert script.success_exit_codes == [5]
