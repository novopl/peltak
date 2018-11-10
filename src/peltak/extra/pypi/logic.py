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
""" pypi related commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
from os.path import join

# local imports
from peltak.core import conf
from peltak.core import fs
from peltak.core import log
from peltak.core import shell
from peltak.core import util


def upload(target):
    # type: (str) -> None
    """ Upload the release to a pypi server.

    TODO: Make sure the git directory is clean before allowing a release.

    Args:
        target (str):
            pypi target as defined in ~/.pypirc
    """
    log.info("Uploading to pypi server <33>{}".format(target))
    with conf.within_proj_dir():
        shell.run('python setup.py sdist register -r "{}"'.format(target))
        shell.run('python setup.py sdist upload -r "{}"'.format(target))


def gen_pypirc(username=None, password=None):
    # type: (str, str) -> None
    """ Generate ~/.pypirc with the given credentials.

    Useful for CI builds. Can also get credentials through env variables
    ``PYPI_USER`` and ``PYPI_PASS``.

    Args:
        username (str):
            pypi username. If not given it will try to take it from the
            `` PYPI_USER`` env variable.
        password (str):
            pypi password. If not given it will try to take it from the
            `` PYPI_PASS`` env variable.
    """
    path = join(conf.getenv('HOME'), '.pypirc')
    username = username or conf.getenv('PYPI_USER', None)
    password = password or conf.getenv('PYPI_PASS', None)

    if username is None or password is None:
        log.err("You must provide $PYPI_USER and $PYPI_PASS")
        sys.exit(1)

    log.info("Generating <94>{}".format(path))

    fs.write_file(path, util.remove_indent('''
        [distutils]
        index-servers = pypi
        
        [pypi]
        repository: https://upload.pypi.org/legacy/
        username: {username}
        password: {password}
        
    '''.format(
        username=username,
        password=password
    )))
