# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest


# local imports
from peltak.extra.scripts.types import Script, ScriptFiles


def test_works():
    script = Script.from_config('test', {
        'about': 'Test script',
        'command': 'echo test',
        'success_exit_codes': [0, 5],
        'files': {
            'paths': ['src'],
        },
    })

    assert script.name == 'test'
    assert script.about == 'Test script'
    assert script.command == 'echo test'
    assert script.success_exit_codes == [0, 5]

    assert isinstance(script.files, ScriptFiles)
    assert script.files.paths == ['src']


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
