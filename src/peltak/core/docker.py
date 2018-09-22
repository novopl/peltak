# -*- coding: utf-8 -*-
""" Helpers for related docker commands. """
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import requests

# local imports
from . import conf
from . import log
from . import shell
from . import versioning


class RegistryClient(object):
    """ Helper class for talking to docker registry. """
    def __init__(self, registry, username, password):
        self.user = username
        self.pw = password
        self.auth = (username, password)
        self.registry_url = 'https://' + registry

    def list_images(self):
        """ List images stored in the registry.

        :return List[str]:
            List of image names.
        """
        r = requests.get(self.registry_url + '/v2/_catalog', auth=self.auth)
        return r.json()['repositories']

    def list_tags(self, image_name):
        """ List all tags for the given image stored in the registry.

        :param str image_name:
            The name of the image to query. The image must be present on the
            registry for this call to return any values.
        :return List[str]:
            List of tags for that image.
        """
        tags_url = self.registry_url + '/v2/{}/tags/list'

        r = requests.get(tags_url.format(image_name), auth=self.auth)
        data = r.json()

        if 'tags' in data:
            return reversed(sorted(data['tags']))

        return []


def build_image(registry, image):
    """ Build docker image.

    :param str registry:
        The name of the registry this image belongs to. If not given, the
        resulting image will have a name without the registry.
    :param Dict image:
        The dict containing the information about the built image. This is the
        same dictionary as defined in DOCKER_IMAGES variable.
    """
    values = {
        'registry': '' if registry is None else registry + '/',
        'image': image['name'],
        'version': versioning.current(),
    }
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
