# -*- coding: utf-8 -*-
""" git flow hotfix commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import sys

# local imports
from peltak.core import shell
from peltak.core import conf
from peltak.core import git
from peltak.core import log
from peltak.core import versioning
from . import common


def start(component, exact):
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

    develop = conf.get('git.devel_branch', 'develop')
    common.assert_on_branch(develop)

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

        common.git_checkout(branch, create=True)

        log.info("Creating commit for the release")
        shell.run('git add {ver_file} && git commit -m "{msg}"'.format(
            ver_file=version_file,
            msg="Releasing v{}".format(new_ver)
        ))


def finish():
    """ Merge current release into develop and master and tag it. """
    if git.staged() or git.unstaged():
        log.err("You have uncommitted changes in your repo!")
        sys.exit(1)

    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('release')

    # Merge release into master
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Merge hotfix into develop
    common.git_checkout(master)
    common.git_pull(master)
    common.git_merge(master, branch.name, no_ff=True)

    # Tag the release commit with version number
    tag()

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(develop)


def merged():
    """ Cleanup the release branch after it was remotely merged to master. """
    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('release')

    # Pull master with the merged release
    common.git_checkout(master)
    common.git_pull(master)

    # Merge to develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(develop)


def tag():
    """ Tag the current commit with the current version. """
    release_ver = versioning.current()
    commit = git.latest_commit()

    with conf.within_proj_dir():
        log.info("Creating tag that marks the release")
        cmd = (
            'git -c "user.name={0.name}" -c "user.email={0.email}" '
            'tag -a "v{1}" -m "Mark v{1} release"'
        ).format(
            commit.author,
            release_ver
        )
        shell.run(cmd)
