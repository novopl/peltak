# -*- coding: utf-8 -*-
""" Commands for building and pushing the app image.

This is mainly for web apps that are deployed with docker.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# 3rd party imports
import click
import requests

# local imports
from peltak.commands import cli
from peltak.core import conf
from peltak.core import log
from peltak.core import shell
from peltak.core import versioning


@cli.group('docker')
def docker_cli():
    """ Commands for building the project docker images. """
    pass


@docker_cli.command('build')
def docker_build():
    """ Build and tag a docker image for the project.

    It requires a DOCKER_IMAGE conf variable to be set and that will be used
    as the name of the image. If DOCKER_REGISTRY is also set, then the
    resulting image will a have name of {registry}/{image}. This will create two
    tags for the image: {name}:{version} and {name}:latest where {name} is the
    image name described above and {version} is the current project version
    (as shown by `peltak version show`). It will assume the Dockerfile is in the
    root project directory, but the location can be customized with DOCKERFILE
    conf variable.
    """
    with conf.within_proj_dir():
        registry = conf.get('DOCKER_REGISTRY')
        values = {
            'registry': '' if registry is None else registry + '/',
            'image': conf.get('DOCKER_IMAGE'),
            'version': versioning.current(),
        }
        args = [
            '-t {registry}{image}'.format(**values),
            '-t {registry}{image}:{version}'.format(**values),
            '-f {}'.format(conf.get('DOCKERFILE', 'Dockerfile'))
        ]
        shell.run('docker build {args} . '.format(args=' '.join(args)))


@docker_cli.command('push')
def docker_push():
    """ Push project docker images to the registry.

    This command requires both DOCKER_IMAGE and DOCKER_REGISTRY conf variables
    to be set. This will push the image built by `peltak docker build` to the
    specified registry. For the details of how the tag name is generated, see
    `peltak docker build --help`.
    """
    registry = conf.get('DOCKER_REGISTRY')
    if registry is None:
        log.err("You must define DOCKER_REGISTRY conf variable to push images")
        sys.exit(-1)

    values = {
        'registry': registry,
        'image': conf.get('DOCKER_IMAGE'),
        'version': versioning.current(),
    }
    tags = [
        '{registry}/{image}'.format(**values),
        '{registry}/{image}:{version}'.format(**values),
    ]

    for tag in tags:
        log.info("Pushing ^35{}".format(tag))
        shell.run('docker push {}'.format(tag))


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
    """
    registry = conf.get('DOCKER_REGISTRY')

    if registry is None:
        log.err("You must define DOCKER_REGISTRY conf variable to list images")
        sys.exit(-1)

    registry_url = 'https://' + registry
    registry_user = conf.get('DOCKER_REGISTRY_USER')

    if registry_user is None:
        registry_user = click.prompt("Username")

    auth = (registry_user, registry_pass)
    r = requests.get(registry_url + '/v2/_catalog', auth=auth)

    tags_url = registry_url + '/v2/{}/tags/list'
    images = {}

    for repo in r.json()['repositories']:
        r = requests.get(tags_url.format(repo), auth=auth)
        images[repo] = reversed(sorted(r.json()['tags']))

    shell.cprint("^32Images in ^34{} ^32registry:^0", registry_url)
    for image, tags in images.items():
        for tag in tags:
            shell.cprint('  {}:^35{}^0', image, tag)
