# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import Mock, patch

# local imports
from peltak.extra.scripts.commands import post_conf_load
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

    p_Script.from_config.side_effects = [p_script_1, p_script_2]

    post_conf_load()

    assert p_Script.from_config.call_count == 2

    p_script_1.register.called_once()
    p_script_2.register.called_once()
