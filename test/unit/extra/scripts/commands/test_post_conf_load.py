# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak.cli.scripts import peltak_cli, post_conf_load
from peltak.testing import patch_pelconf


@patch_pelconf({
    'scripts': {
        'fake1': {'command': 'fake1_cmd'},
        'fake2': {'command': 'fake2_cmd'},
    }
})
@patch('peltak.core.scripts.types.Script')
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
        'fake1': {'command': 'fake1_cmd', 'peltak_cli': True},
    }
})
@patch('peltak.core.scripts.types.Script')
def test_attaches_to_peltak_cli_if_peltak_cli_is_True(p_Script):
    p_script = Mock()
    p_script.peltak_cli = True

    p_Script.from_config.return_value = p_script

    post_conf_load()

    p_script.register.assert_called_once_with(peltak_cli)
