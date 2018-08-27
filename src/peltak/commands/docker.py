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

    It requires a DOCKER_IMAGES conf variable to be set and contain the
    definitions for all the images built by the project. If DOCKER_REGISTRY is
    also set, then the resulting images will a have name of
    ``<registry>/<image>``. This will create two tags for each image:
    ``<name>:<version>`` and ``<name>:latest`` where <name> is the image name
    as specified in DOCKER_IMAGES entry and <version> is the current project
    version (as shown by ``peltak version``).

    Config example::

        \b
        conf.init({
            'DOCKER_REGISTRY': 'registry.mydomain.com',
            'DOCKER_IMAGES': [
                {'name': 'myapp',}
            ]
        })

    Example::

        \b
        $ peltak docker build

    """
    from peltak.core import conf
    from peltak.core import docker

    registry = conf.get('DOCKER_REGISTRY')
    docker_images = conf.get('DOCKER_IMAGES', [])

    for image in docker_images:
        docker.build_image(registry, image)


@docker_cli.command('push')
def push_images():
    """ Push project docker images to the registry.

    This command requires both DOCKER_IMAGES and DOCKER_REGISTRY conf variables
    to be set. This will push the images built by ``peltak docker build`` to the
    specified registry. For the details of how the names and tags are generated,
    see ``peltak docker build --help``.

    Config example::

        \b
        conf.init({
            'DOCKER_REGISTRY': 'registry.mydomain.com',
            'DOCKER_IMAGES': [
                {'name': 'myapp',}
            ]
        })

    Example::

        \b
        $ peltak docker push

    """
    import sys
    from peltak.core import conf
    from peltak.core import docker
    from peltak.core import log

    registry = conf.get('DOCKER_REGISTRY')
    docker_images = conf.get('DOCKER_IMAGES', [])

    if registry is None:
        log.err("You must define DOCKER_REGISTRY conf variable to push images")
        sys.exit(-1)

    for image in docker_images:
        docker.push_image(registry, image)


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

    This command requires the DOCKER_REGISTRY conf variable to be set. You can
    also hard-code the username with the DOCKER_REGISTRY_USER conf variable. You
    will be asked for the password every time though for security reasons.

    Config example::

        \b
        conf.init({
            'DOCKER_REGISTRY': 'registry.mydomain.com',
            'DOCKER_REGISTRY_USER': 'myuser'
        })

    Example::

        \b
        $ peltak docker list            # List images in the docker registry
        $ peltak docker list -p mypass  # List registry images, use give pw

    """
    import sys
    from peltak.core import conf
    from peltak.core import docker
    from peltak.core import log
    from peltak.core import shell

    registry = conf.get('DOCKER_REGISTRY', None)

    if registry is None:
        log.err("You must define DOCKER_REGISTRY conf variable to list images")
        sys.exit(-1)

    registry_user = conf.get('DOCKER_REGISTRY_USER', None)

    if registry_user is None:
        registry_user = click.prompt("Username")

    rc = docker.RegistryClient(registry, registry_user, registry_pass)
    images = {x: rc.list_tags(x) for x in rc.list_images()}

    shell.cprint("<32>Images in <34>{} <32>registry:", registry)
    for image, tags in images.items():
        shell.cprint('  <92>{}', image)
        for tag in tags:
            shell.cprint('      <90>{}:<35>{}', image, tag)
