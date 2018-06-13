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
from peltak.core import git, log, conf, version as ver
from . import cli


VERSION_FILE = conf.get_path('VERSION_FILE', 'VERSION')


@cli.group('release')
def rel():
    """ Release related commands. """
    pass

@cli.group('version')
def ver_cmd():
    """ Versioning related commands. """
    pass


@ver_cmd.command('show')
def version():
    """ Return current project version. """
    current = ver.get_current(VERSION_FILE)

    log.info("Version: ^35{}".format(current))


@ver_cmd.command('bump')
@click.argument('component', required=False, default='patch')
@click.option('--exact', type=str)
def bump_version(component='patch', exact=None):
    """ Bump current project version without committing anything.

    No tags are created either.
    """
    log.info("Bumping package version")

    old_ver = ver.get_current(VERSION_FILE)
    log.info("  old version: ^35{}".format(old_ver))

    if ver.is_valid(exact):
        new_ver = exact
    else:
        new_ver = ver.bump(old_ver, component)

    with open(VERSION_FILE, 'w') as fp:
        fp.write(new_ver)

    log.info("  new version: ^35{}".format(new_ver))


@rel.command('make')
@click.argument('component', required=False)
@click.option('--exact', type=str)
def make_release(component='patch', exact=None):
    """ Release a new version of the project.

    This will bump the version number (patch component by default) + add and tag
    a commit with that change. Finally it will upload the package to pypi.

    1. Bump version.
    2. Create and checkout release/* branch
    3. Create commit with bumped version.
    """
    with conf.within_proj_dir(quiet=True):
        out = conf.run('git status --porcelain', capture=True).strip()
        has_changes = any(
            not l.startswith('??') for l in out.split(os.linesep) if l.strip()
        )

    if has_changes:
        log.info("Cannot release: there are uncommitted changes")
        exit(1)

    log.info("Bumping package version")
    old_ver = ver.get_current(VERSION_FILE)

    if ver.is_valid(exact):
        new_ver = exact
    else:
        new_ver = ver.bump(old_ver, component)

    with open(VERSION_FILE, 'w') as fp:
        fp.write(new_ver)

    log.info("  old version: ^35{}".format(old_ver))
    log.info("  new version: ^35{}".format(new_ver))

    with conf.within_proj_dir(quiet=True):
        branch = 'release/' + new_ver

        log.info("Checking out new branch ^35{}", branch)
        conf.run('git checkout -b ' + branch)

        log.info("Creating commit for the release")
        conf.run('git add {ver_file} && git commit -m "Release: v{ver}"'.format(
            ver_file=VERSION_FILE,
            ver=new_ver
        ))


@rel.command('tag')
def tag_release():
    """ Create a new release tag for the current version. """
    release_ver = ver.get_current(VERSION_FILE)
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
        conf.run(cmd)


@rel.command()
@click.argument('target', required=False)
def upload(target='local'):
    """ Release to a given pypi server ('local' by default). """
    log.info("Uploading to pypi server ^33{}".format(target))
    with conf.within_proj_dir(quiet=False):
        conf.run('python setup.py sdist register -r "{}"'.format(target))
        conf.run('python setup.py sdist upload -r "{}"'.format(target))


@rel.command()
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
