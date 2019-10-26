# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import Mock, patch


@patch('peltak.core.pelconf.Pelconf.init')
def test_loads_config_when_module_is_imported(p_pelconf_init):
    # type: (Mock) -> None

    import peltak.main  # pylint: disable=unused-import,unused-variable

    p_pelconf_init.assert_called_once()


# Used only in type hint comments
del Mock
