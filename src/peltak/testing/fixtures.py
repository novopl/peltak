from pathlib import Path
from unittest.mock import patch

import pytest

from peltak.core import conf
from .util import TestDataProvider


REPO_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = REPO_DIR / 'test' / 'data'


@pytest.fixture
def app_conf():
    appconf = conf.Config()
    with patch('peltak.core.conf.g_conf', appconf):
        yield appconf


@pytest.fixture()
def test_data():
    """ Returns a context manager to work within temporary test project.

    This ensures each test has a clean copy of the data.

    :return testing.TestDataProvider:
        TestDataProvider instance that can be used to simulate working within
        one of the test data directories.
    """
    return TestDataProvider(DATA_DIR)
