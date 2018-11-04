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
""" Docker commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
from typing import Any, Dict

# 3rd party imports
import click

# local imports
from peltak.core import shell
from peltak.core import log
from peltak.core import conf
from peltak.core import versioning
from . import client


def build_images():
    # type: () -> None
    """ Build all docker images for the project. """
    registry = conf.get('docker.registry')
    docker_images = conf.get('docker.images', [])

    for image in docker_images:
        build_image(registry, image)


def push_images():
    # type: () -> None
    """ Push all project docker images to a remote registry. """
    registry = conf.get('docker.registry')
    docker_images = conf.get('docker.images', [])

    if registry is None:
        log.err("You must define docker.registry conf variable to push images")
        sys.exit(-1)

    for image in docker_images:
        push_image(registry, image)


def docker_list(registry_pass):
    # type: (str) -> None
    """ List docker images stored in the remote registry.

    Args:
        registry_pass (str):
            Remote docker registry password.
    """
    registry = conf.get('docker.registry', None)

    if registry is None:
        log.err("You must define docker.registry conf variable to list images")
        sys.exit(-1)

    registry_user = conf.get('docker.registry_user', None)

    if registry_user is None:
        registry_user = click.prompt("Username")

    rc = client.RegistryClient(registry, registry_user, registry_pass)
    images = {x: rc.list_tags(x) for x in rc.list_images()}

    shell.cprint("<32>Images in <34>{} <32>registry:", registry)
    for image, tags in images.items():
        shell.cprint('  <92>{}', image)
        for tag in tags:
            shell.cprint('      <90>{}:<35>{}', image, tag)


def build_image(registry, image):
    # type: (str, Dict[str, Any]) -> None
    """ Build docker image.

    Args:
        registry (str):
            The name of the registry this image belongs to. If not given, the
            resulting image will have a name without the registry.
        image (dict[str, Any]):
            The dict containing the information about the built image. This is
            the same dictionary as defined in DOCKER_IMAGES variable.
    """
    if ':' in image['name']:
        _, tag = image['name'].split(':', 1)
    else:
        _, tag = image['name'], None

    values = {
        'registry': '' if registry is None else registry + '/',
        'image': image['name'],
        'tag': tag,
    }

    if tag is None:
        args = [
            '-t {registry}{image}'.format(**values),
            '-t {registry}{image}:{version}'.format(
                version=versioning.current(),
                **values
            ),
        ]
    else:
        args = ['-t {registry}{image}'.format(**values)]

    if 'file' in image:
        args.append('-f {}'.format(conf.proj_path(image['file'])))

    with conf.within_proj_dir(image.get('path', '.')):
        log.info("Building <33>{registry}<35>/{image}", **values)
        shell.run('docker build {args} .'.format(args=' '.join(args)))


def push_image(registry, image):
    # type: (str, Dict[str, Any]) -> None
    """ Push the given image to selected repository.

    Args:
        registry (str):
            The name of the registry we're pushing to. This is the address of
            the repository without the protocol specification (no http(s)://)
        image (dict[str, Any]):
            The dict containing the information about the image. This is the
            same dictionary as defined in DOCKER_IMAGES variable.
    """
    values = {
        'registry': registry,
        'image': image['name'],
    }

    log.info("Pushing <33>{registry}<35>/{image}".format(**values))
    shell.run('docker push {registry}/{image}'.format(**values))


# Used in docstrings only until we drop python2 support
del Any, Dict
