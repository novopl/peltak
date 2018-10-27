# -*- coding: utf-8 -*-
""" pypi related commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
from os.path import join

# local imports
from peltak.core import shell
from peltak.core import conf
from peltak.core import log


def upload(target):
    """ Upload the release to a pypi server.

    TODO: Make sure the git directory is clean before allowing a release.

    :param str target:
        pypi target as defined in ~/.pypirc
    """
    log.info("Uploading to pypi server <33>{}".format(target))
    with conf.within_proj_dir():
        shell.run('python setup.py sdist register -r "{}"'.format(target))
        shell.run('python setup.py sdist upload -r "{}"'.format(target))


def gen_pypirc(username=None, password=None):
    """ Generate ~/.pypirc with the given credentials.

    Useful for CI builds. Can also get credentials through env variables
    ``PYPI_USER`` and ``PYPI_PASS``.

    :param str username:
        pypi username.
    :param str password:
        pypi password.
    """
    path = join(conf.getenv('HOME'), '.pypirc')
    username = username or conf.getenv('PYPI_USER', None)
    password = password or conf.getenv('PYPI_PASS', None)

    if username is None or password is None:
        log.err("You must provide $PYPI_USER and $PYPI_PASS")
        sys.exit(1)

    log.info("Generating .pypirc config <94>{}".format(path))

    with open(path, 'w') as fp:
        fp.write('\n'.join((
            '[distutils]',
            'index-servers = ',
            '    pypi',
            '',
            '[pypi]',
            'repository: https://upload.pypi.org/legacy/',
            'username: {}'.format(username),
            'password: {}'.format(password),
            '',
        )))
