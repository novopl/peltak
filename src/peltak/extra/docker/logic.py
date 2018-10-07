# -*- coding: utf-8 -*-
""" Helpers for docker related commands. """
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.core import log
from peltak.core import shell
from peltak.core import versioning


def build_image(registry, image):
    """ Build docker image.

    :param str registry:
        The name of the registry this image belongs to. If not given, the
        resulting image will have a name without the registry.
    :param Dict image:
        The dict containing the information about the built image. This is the
        same dictionary as defined in DOCKER_IMAGES variable.
    """
    if ':' in image['name']:
        name, tag = image['name'].split(':', 1)
    else:
        name, tag = image['name'], None

    values = {
        'registry': '' if registry is None else registry + '/',
        'image': name,
        'tag': tag,
        'version': versioning.current(),
    }

    if tag is not None:
        args = [
            '-t {registry}{image}:{tag}'.format(**values),
        ]
    else:
        args = [
            '-t {registry}{image}'.format(**values),
            '-t {registry}{image}:{version}'.format(**values),
        ]

    if 'file' in image:
        args.append('-f {}'.format(conf.proj_path(image['file'])))

    with conf.within_proj_dir(image.get('path', '.')):
        log.info("Building <33>{registry}<35>/{image}".format(**values))
        shell.run('docker build {args} .'.format(args=' '.join(args)))


def push_image(registry, image):
    """ Push the given image to selected repository.

    :param str registry:
        The name of the registry we're pushing to. This is the address of the
        repository without the protocol specification (no http(s)://)
    :param Dict image:
        The dict containing the information about the image. This is the same
        dictionary as defined in DOCKER_IMAGES variable.
    """
    values = {
        'registry': registry,
        'image': image['name'],
    }

    log.info("Pushing <33>{registry}<35>/{image}".format(**values))
    shell.run('docker push {registry}/{image}'.format(**values))
