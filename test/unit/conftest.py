# -*- coding: utf-8 -*-
""" pytest setup """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import dirname, join, relpath

# 3rd party imports
import pytest

# local imports
from peltak import testing


DATA_DIR = join(dirname(dirname(__file__)), 'data')


def pytest_itemcollected(item):
    """ Prettier test names. """
    name = item.originalname or item.name
    if name.startswith('test_'):
        name = name[5:]

    name = name.replace('_', ' ').strip()
    name = name[0].upper() + name[1:]

    rel_path = relpath(item.fspath.strpath, dirname(item.fspath.dirname))
    item._nodeid = '{location:50} {name}'.format(
        name=name,
        location='{}:{}'.format(rel_path, item.location[1]),
    )


@pytest.fixture()
def test_data():
    """ Returns a context manager to work within temporary test project.

    This ensures each test has a clean copy of the data.

    :return testing.TestDataProvider:
        TestDataProvider instance that can be used to simulate working within
        one of the test data directories.
    """
    return testing.TestDataProvider(DATA_DIR)


# pylint: disable=unused-import,wildcard-import,unused-wildcard-import
# Import all peltak fixtures
from peltak.testing.fixtures import *   # noqa