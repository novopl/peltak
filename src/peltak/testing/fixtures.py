from unittest.mock import patch

import pytest

from peltak.core import conf


@pytest.fixture
def app_conf():
    appconf = conf.Config()
    with patch('peltak.core.conf.g_conf', appconf):
        yield appconf
