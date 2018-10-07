# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.extra.docker.client import RegistryClient


def test_works_as_expected():
    client = RegistryClient('docker.example.com', 'john', 'secret99')

    assert client.user == 'john'
    assert client.pw == 'secret99'
    assert client.auth == ('john', 'secret99')
    assert client.registry_url == 'https://docker.example.com'
