# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import Mock, patch


@patch('requests.get')
def test_works_as_expected(p_get, registry_client):
    p_get.json = Mock(return_value={'repositories': []})

    registry_client.list_images()

    p_get.assert_called_once_with(
        registry_client.registry_url + '/v2/_catalog',
        auth=registry_client.auth
    )
