# -*- coding: utf-8 -*-
""" Release commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
import os
from fnmatch import fnmatch
from os.path import join

# local imports
from peltak.core import shell
from peltak.core import conf
from peltak.core import git
from peltak.core import log
from peltak.core import versioning


def release(component, exact):
    """ Create a new release branch.

    :param str component:
        Version component to bump when creating the release. Can be *major*,
        *minor* or *patch*.
    :param str exact:
        The exact version to set for the release. Overrides the component
        argument. This allows to re-release a version if something went wrong
        with the release upload.
    """
    version_file = conf.get_path('version_file', 'VERSION')

    with conf.within_proj_dir():
        out = shell.run('git status --porcelain', capture=True).stdout
        lines = out.split(os.linesep)
        has_changes = any(
            not l.startswith('??') for l in lines if l.strip()
        )

    if has_changes:
        log.info("Cannot release: there are uncommitted changes")
        exit(1)

    old_ver, new_ver = versioning.bump(component, exact)

    log.info("Bumping package version")
    log.info("  old version: <35>{}".format(old_ver))
    log.info("  new version: <35>{}".format(new_ver))

    with conf.within_proj_dir():
        branch = 'release/' + new_ver

        log.info("Checking out new branch <35>{}", branch)
        shell.run('git checkout -b ' + branch)

        log.info("Creating commit for the release")

        shell.run('git add {ver_file} && git commit -m "{msg}"'.format(
            ver_file=version_file,
            msg="Releasing v{}".format(new_ver)
        ))


def tag_release():
    """ Tag the current commit with the release version. """
    release_ver = versioning.current()
    author = git.commit_author()

    with conf.within_proj_dir():
        log.info("Creating tag that marks the release")
        cmd = (
            'git -c "user.name={0.name}" -c "user.email={0.email}" '
            'tag -a "v{1}" -m "Mark v{1} release"'
        ).format(
            author,
            release_ver
        )
        shell.run(cmd)


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


def merged():
    """ Cleanup the release branch after it was remotely merged to master. """
    develop_branch = conf.get('develop_branch', 'develop')
    master_branch = conf.get('master_branch', 'master')
    protected_branches = conf.get(
        'protected_branches',
        (master_branch, develop_branch)
    )
    release_branch_pattern = conf.get('release_branch_pattern', 'release/*')
    branch = git.current_branch()

    if not fnmatch(branch, release_branch_pattern):
        log.err("You can only merge from release branches. You can specify "
                "The release branch pattern with RELEASE_BRANCH_PATTERN "
                "conf variable (defaults to release/*).")
        sys.exit(1)

    try:
        shell.run('git rev-parse --verify {}'.format(branch))
    except IOError:
        log.err("Branch '{}' does not exist".format(branch))

    # Checkout develop and merge the release
    log.info("Checking out <33>{}".format(develop_branch))
    shell.run('git checkout {}'.format(develop_branch))

    log.info("Merging <35>{} <32>into <33>{}".format(branch, develop_branch))
    shell.run('git merge {}'.format(branch))

    log.info("Checking out <33>{}".format(master_branch))
    shell.run('git checkout {}'.format(master_branch))

    log.info("Pulling latest changes")
    shell.run('git pull origin {}'.format(master_branch))

    if branch not in protected_branches:
        log.info("Deleting branch <35>{}".format(branch))
        shell.run('git branch -d {}'.format(branch))

    log.info("Pruning")
    shell.run('git fetch --prune origin')

    log.info("Checking out <33>{}<32> branch".format(develop_branch))
    shell.run('git checkout {}'.format(develop_branch))
