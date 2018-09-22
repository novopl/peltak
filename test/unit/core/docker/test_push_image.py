# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party
import pytest
from mock import patch, Mock, MagicMock

# local imports
from peltak.core import docker


@pytest.mark.parametrize('image,expected_cmd', [
    ({'name': 'fakeimg'}, 'docker push {reg}/{img}'),
])
@patch('peltak.core.shell.run')
@patch('peltak.core.versioning.current', Mock(return_value='9.9.9'))
@patch('peltak.core.conf.within_proj_dir', MagicMock())
def test_push_image_generates_proper_shell_command(p_run, image, expected_cmd):
    registry = 'fake.test.com'

    docker.push_image(registry, image)

    p_run.assert_called_once_with(expected_cmd.format(
        reg=registry,
        img=image['name'],
        ver='9.9.9',
    ))
