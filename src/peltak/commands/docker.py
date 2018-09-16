# -*- coding: utf-8 -*-
""" Commands for building and pushing the app image.

This is mainly for web apps that are deployed with docker.
"""
from __future__ import absolute_import
from . import cli, click


@cli.group('docker')
def docker_cli():
    """ Commands for building the project docker images. """
    pass


@docker_cli.command('build')
def build_images():
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
        conf.init({
            'docker': {
                'registry': 'registry.mydomain.com',
                'images': [
                    {'name': 'myapp'}
                ]
            }
        })

    Example::

        \b
        $ peltak docker build

    """
    from .impl import docker

    docker.build_images()


@docker_cli.command('push')
def push_images():
    """ Push project docker images to the registry.

    This command requires both docker.images and docker.registry conf variables
    to be set. This will push the images built by ``peltak docker build`` to the
    specified registry. For the details of how the names and tags are generated,
    see ``peltak docker build --help``.

    Config example::

        \b
        conf.init({
            'docker': {
                'registry': 'registry.mydomain.com',
                'images': [
                    {'name': 'myapp'}
                ]
            }
        })

    Example::

        \b
        $ peltak docker push

    """
    from .impl import docker

    docker.push_images()


@docker_cli.command('list')
@click.option(
    '-p', '--password', 'registry_pass',
    type=str,
    prompt='Password',
    hide_input=True,
    help='Registry password'
)
def docker_list(registry_pass):
    """ List docker images and their tags on the remote registry.

    This command requires the docker.registry conf variable to be set. You can
    also hard-code the username with the docker.registry_user conf variable. You
    will be asked for the password every time though for security reasons.

    Config example::

        \b
        conf.init({
            'docker': {
                'registry': 'registry.mydomain.com',
                'registry_user': 'myuser'
            }
        })

    Example::

        \b
        $ peltak docker list            # List images in the docker registry
        $ peltak docker list -p mypass  # List registry images, use give pw

    """
    from .impl import docker

    docker.docker_list(registry_pass)
