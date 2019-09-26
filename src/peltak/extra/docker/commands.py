# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
#################
``peltak docker``
#################

Commands for building and pushing the app image.

This is mainly for web apps that are deployed with docker.
"""
from __future__ import absolute_import

# local imports
from peltak.commands import root_cli, click


@root_cli.group('docker')
def docker_cli():
    # type: () -> None
    """ Commands for building the project docker images. """
    pass


@docker_cli.command('list')
@click.option(
    '-p', '--password', 'registry_pass',
    type=str,
    prompt='Password',
    hide_input=True,
    help='Registry password'
)
def docker_list(registry_pass):
    # type: (str) -> None
    """ List docker images and their tags on the remote registry.

    This command requires the docker.registry conf variable to be set. You can
    also hard-code the username with the docker.registry_user conf variable. You
    will be asked for the password every time though for security reasons.

    Config example::

        \b
        docker:
          registry: 'registry.mydomain.com'
          registry_user: 'myuser'
          images:
            - name: 'myapp:1.0'
              path: '.'
              file: 'Dockerfile'

    Example::

        \b
        $ peltak docker list            # List images in the docker registry
        $ peltak docker list -p mypass  # List registry images, use given pw

    """
    from . import logic

    logic.docker_list(registry_pass)
