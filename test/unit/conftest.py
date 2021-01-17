# Import all fixtures
from pathlib import Path

import pytest

from peltak import testing
from peltak.testing.fixtures import *   # noqa pylint: disable=wildcard-import unused-import unused-wildcard-import


@pytest.fixture
def unit_test_data():
    yield testing.DataLoader(Path(__file__).parent / '_data')
