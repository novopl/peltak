# -*- coding: utf-8 -*-
""" Various fixtures useful for testing.

All of those will be automatically imported for all unit tests.
"""
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import docker


@pytest.fixture()
def registry_client():
    """ Return fake RegistryClient
    :return docker.RegistryClient:
        Fake registry client
    """
    return docker.RegistryClient('docker.example.com', 'john', 'secret99')
