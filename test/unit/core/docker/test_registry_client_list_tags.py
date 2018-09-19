# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch

# local imports
from peltak import testing


@patch('requests.get')
def test_parses_registry_response_properly(p_get, registry_client):
    p_get.return_value = testing.mock_response({'tags': ['tag1', 'tag2']})

    tags = registry_client.list_tags('fakeimg')

    p_get.assert_called_once_with(
        registry_client.registry_url + '/v2/fakeimg/tags/list',
        auth=registry_client.auth
    )

    assert frozenset(tags) == frozenset(('tag1', 'tag2'))


@patch('requests.get')
def test_returns_empty_array_if_cant_find_tags_in_the_response(p_get,
                                                               registry_client):
    p_get.return_value = testing.mock_response({})

    tags = registry_client.list_tags('fakeimg')

    p_get.assert_called_once_with(
        registry_client.registry_url + '/v2/fakeimg/tags/list',
        auth=registry_client.auth
    )

    assert tags == []
