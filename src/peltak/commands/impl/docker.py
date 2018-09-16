# -*- coding: utf-8 -*-
""" Docker commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# 3rd party imports
import click

# local imports
from peltak.core import shell
from peltak.core import log
from peltak.core import conf
from peltak.core import docker


def build_images():
    """ Build all docker images for the project. """
    registry = conf.get('docker.registry')
    docker_images = conf.get('docker.images', [])

    for image in docker_images:
        docker.build_image(registry, image)


def push_images():
    """ Push all project docker images to a remote registry. """
    registry = conf.get('docker.registry')
    docker_images = conf.get('docker.images', [])

    if registry is None:
        log.err("You must define docker.registry conf variable to push images")
        sys.exit(-1)

    for image in docker_images:
        docker.push_image(registry, image)


def docker_list(registry_pass):
    """ List docker images stored in the remote registry. """
    registry = conf.get('docker.registry', None)

    if registry is None:
        log.err("You must define docker.registry conf variable to list images")
        sys.exit(-1)

    registry_user = conf.get('docker.registry_user', None)

    if registry_user is None:
        registry_user = click.prompt("Username")

    rc = docker.RegistryClient(registry, registry_user, registry_pass)
    images = {x: rc.list_tags(x) for x in rc.list_images()}

    shell.cprint("<32>Images in <34>{} <32>registry:", registry)
    for image, tags in images.items():
        shell.cprint('  <92>{}', image)
        for tag in tags:
            shell.cprint('      <90>{}:<35>{}', image, tag)
