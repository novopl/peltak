# -*- coding: utf-8 -*-
"""
Helper commands for releasing to pypi.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import sys
from os.path import join
from warnings import warn

# 3rd party modules
import click

# local imports
from peltak.core import shell
from peltak.core import conf
from peltak.core import git
from peltak.core import log
from peltak.core import versioning
from . import cli


VERSION_FILE = conf.get_path('VERSION_FILE', 'VERSION')


@cli.group('release')
def rel():
    """ Release related commands. """
    pass


@rel.command('make')
@click.argument(
    'component',
    type=click.Choice(['major','minor', 'patch']),
    required=False,
    default='patch'
)
@click.option('--exact', type=str)
def make_release(component, exact):
    """ Release a new version of the project.

    This will bump the version number (patch component by default) + add and tag
    a commit with that change. Finally it will upload the package to pypi.

    1. Bump version.
    2. Create and checkout release/* branch
    3. Create commit with bumped version.
    """
    with conf.within_proj_dir(quiet=True):
        out = shell.run('git status --porcelain', capture=True).stdout
        has_changes = any(
            not l.startswith('??') for l in out.split(os.linesep) if l.strip()
        )

    if has_changes:
        log.info("Cannot release: there are uncommitted changes")
        exit(1)

    old_ver, new_ver = versioning.bump(component, exact)

    log.info("Bumping package version")
    log.info("  old version: ^35{}".format(old_ver))
    log.info("  new version: ^35{}".format(new_ver))

    with conf.within_proj_dir(quiet=True):
        branch = 'release/' + new_ver

        log.info("Checking out new branch ^35{}", branch)
        shell.run('git checkout -b ' + branch)

        log.info("Creating commit for the release")

        shell.run('git add {ver_file} && git commit -m "{msg}"'.format(
            ver_file=VERSION_FILE,
            msg="Release: v{}".format(new_ver)
        ))


@rel.command('tag')
def tag_release():
    """ Create a new release tag for the current version. """
    release_ver = versioning.current()
    author = git.commit_author()

    with conf.within_proj_dir(quiet=False):
        log.info("Creating tag that marks the release")
        cmd = (
            'git -c "user.name={0.name}" -c "user.email={0.email}" '
            'tag -a "v{1}" -m "Mark v{1} release"'
        ).format(
            author,
            release_ver
        )
        shell.run(cmd)


@rel.command()
@click.argument('target')
def upload(target):
    """ Release to a given pypi server ('local' by default). """
    log.info("Uploading to pypi server ^33{}".format(target))
    with conf.within_proj_dir(quiet=False):
        shell.run('python setup.py sdist register -r "{}"'.format(target))
        shell.run('python setup.py sdist upload -r "{}"'.format(target))


@rel.command('gen-pypirc')
@click.argument('username', required=False)
@click.argument('password', required=False)
def gen_pypirc(username=None, password=None):
    """ Generate .pypirc config with the given credentials. """
    path = join(conf.getenv('HOME'), '.pypirc')
    username = username or conf.getenv('PYPI_USER', None)
    password = password or conf.getenv('PYPI_PASS', None)

    if username is None or password is None:
        log.err("You must provide $PYPI_USER and $PYPI_PASS")
        sys.exit(1)

    log.info("Generating .pypirc config ^94{}".format(path))

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
