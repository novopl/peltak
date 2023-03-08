# pylint: disable=missing-docstring
from unittest.mock import Mock, patch


@patch('peltak.core.conf.init')
def test_loads_config_when_module_is_imported(p_conf_init: Mock):
    import peltak.main  # noqa F401

    p_conf_init.assert_called_once()
