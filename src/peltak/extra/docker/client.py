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
""" Docker registry client. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Iterator, List, Tuple


class RegistryClient(object):
    """ Helper class for talking to docker registry.

    Attributes:
        user (str):
            Docker registry user name.
        pw (str):
            Docker registry password.
        auth (tuple[str, str]):
            Tuple of ``(self.user, self.pw)`` for easier access.
        registry_url (str):
            The remote registry URL.
    """
    def __init__(self, registry, username, password):
        self.user = username                        # type: str
        self.pw = password                          # type: str
        self.auth = (username, password)            # type: Tuple[str, str]
        self.registry_url = 'https://' + registry   # type: str

    def get(self, *args, **kw):
        # type: (*Any, *Any) -> requests.Response
        """ Proxy over requests.get

        Do not include requests globally so it's not required to build and
        push images. Otherwise, the project needs to install requests even
        when not using registry in any way.
        """
        import requests
        return requests.get(*args, **kw)

    def list_images(self):
        # type: () -> List[str]
        """ List images stored in the registry.

        Returns:
            list[str]: List of image names.
        """
        r = self.get(self.registry_url + '/v2/_catalog', auth=self.auth)
        return r.json()['repositories']

    def list_tags(self, image_name):
        # type: (str) -> Iterator[str]
        """ List all tags for the given image stored in the registry.

        Args:
            image_name (str):
                The name of the image to query. The image must be present on the
                registry for this call to return any values.
        Returns:
            list[str]: List of tags for that image.
        """
        tags_url = self.registry_url + '/v2/{}/tags/list'

        r = self.get(tags_url.format(image_name), auth=self.auth)
        data = r.json()

        if 'tags' in data:
            return reversed(sorted(data['tags']))

        return []


# Used in docstrings only until we drop python2 support
del Any, Iterator, List, Tuple
