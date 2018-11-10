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
""" Commands for building and pushing the app image.

This is mainly for web apps that are deployed with docker.
"""
from __future__ import absolute_import

from peltak.commands import root_cli, click, pretend_option


@root_cli.group('docker')
def docker_cli():
    # type: () -> None
    """ Commands for building the project docker images. """
    pass


@docker_cli.command('build')
@pretend_option
def build_images():
    # type: () -> None
    """ Build and tag a docker image for the project.

    It requires a docker.images conf variable to be set and contain the
    definitions for all the images built by the project. If docker.registry is
    also set, then the resulting images will a have name of
    ``<registry>/<image>``. This will create two tags for each image:
    ``<name>:<version>`` and ``<name>:latest`` where <name> is the image name
    as specified in docker.images entry and <version> is the current project
    version (as shown by ``peltak version``).

    Config example::

        \b
        docker:
          registry: 'registry.mydomain.com'
          images:
            - name: 'myapp:1.0'
              path: '.'
              file: 'Dockerfile'

    Example::

        \b
        $ peltak docker build

    """
    from . import logic

    logic.build_images()


@docker_cli.command('push')
@pretend_option
def push_images():
    # type: () -> None
    """ Push project docker images to the registry.

    This command requires both docker.images and docker.registry conf variables
    to be set. This will push the images built by ``peltak docker build`` to the
    specified registry. For the details of how the names and tags are generated,
    see ``peltak docker build --help``.

    Config example::

        \b
        docker:
          registry: 'registry.mydomain.com'
          images:
            - name: 'myapp:1.0'
              path: '.'
              file: 'Dockerfile'

    Example::

        \b
        $ peltak docker push

    """
    from . import logic

    logic.push_images()


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
        $ peltak docker list -p mypass  # List registry images, use give pw

    """
    from . import logic

    logic.docker_list(registry_pass)
