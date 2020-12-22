""" pytest setup """
from os.path import dirname, join

import pytest

from peltak import testing


DATA_DIR = join(dirname(dirname(__file__)), 'data')


@pytest.fixture()
def test_data():
    """ Returns a context manager to work within temporary test project.

    This ensures each test has a clean copy of the data.

    :return testing.TestDataProvider:
        TestDataProvider instance that can be used to simulate working within
        one of the test data directories.
    """
    return testing.TestDataProvider(DATA_DIR)


# Import all fixtures
from peltak.testing.fixtures import *   # noqa pylint: disable=wildcard-import unused-import unused-wildcard-import
