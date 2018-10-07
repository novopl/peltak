# -*- coding: utf-8 -*-
""" Docker registry client. """
from __future__ import absolute_import, unicode_literals


class RegistryClient(object):
    """ Helper class for talking to docker registry. """
    def __init__(self, registry, username, password):
        self.user = username
        self.pw = password
        self.auth = (username, password)
        self.registry_url = 'https://' + registry

    def get(self, *args, **kw):
        """ Proxy over requests.get

        Do not include requests globally so it's not required to build and
        push images. Otherwise, the project needs to install requests even
        when not using registry in any way.
        """
        import requests
        return requests.get(*args, **kw)

    def list_images(self):
        """ List images stored in the registry.

        :return List[str]:
            List of image names.
        """
        r = self.get(self.registry_url + '/v2/_catalog', auth=self.auth)
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

        r = self.get(tags_url.format(image_name), auth=self.auth)
        data = r.json()

        if 'tags' in data:
            return reversed(sorted(data['tags']))

        return []
