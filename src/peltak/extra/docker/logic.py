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

# 3rd party imports
import click

# local imports
from peltak.core import shell
from peltak.core import log
from peltak.core import conf
from . import client


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
