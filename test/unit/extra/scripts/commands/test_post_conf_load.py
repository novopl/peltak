# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import Mock, patch

# local imports
from peltak.extra.scripts.commands import post_conf_load, root_cli
from peltak.testing import patch_pelconf


@patch_pelconf({
    'scripts': {
        'fake1': {'command': 'fake1_cmd'},
        'fake2': {'command': 'fake2_cmd'},
    }
})
@patch('peltak.extra.scripts.commands.Script')
def test_works(p_Script):
    p_script_1 = Mock()
    p_script_2 = Mock()

    p_Script.from_config.side_effect = [p_script_1, p_script_2]

    post_conf_load()

    assert p_Script.from_config.call_count == 2

    p_script_1.register.assert_called_once()
    p_script_2.register.assert_called_once()


@patch_pelconf({
    'scripts': {
        'fake1': {'command': 'fake1_cmd', 'root_cli': True},
    }
})
@patch('peltak.extra.scripts.commands.Script')
def test_attaches_to_root_cli_if_root_cli_is_True(p_Script):
    p_script = Mock()
    p_script.root_cli = True

    p_Script.from_config.return_value = p_script

    post_conf_load()

    p_script.register.assert_called_once_with(root_cli)
