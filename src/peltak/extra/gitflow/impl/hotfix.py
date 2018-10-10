# -*- coding: utf-8 -*-
""" git flow hotfix commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# local imports
from peltak.core import conf
from peltak.core import git
from peltak.core import log
from . import common


def start(name):
    """ Start working on a new hotfix.

    This will create a new branch off master called hotfix/<name>.

    :param str name:
        The name of the new feature.
    """
    hotfix_branch = 'hotfix/' + common.to_branch_name(name)
    master = conf.get('git.master_branch', 'master')

    common.assert_on_branch(master)
    common.git_checkout(hotfix_branch, create=True)


def rename(name):
    """ Give the currently developed feature a new name.

    :param str name:
        The new name of the current feature. The current branch will be
        renamed to 'feature/<new_name>'.
    """
    common.assert_branch_type('hotfix')
    common.git_branch_rename('hotfix/' + name.strip().replace(' ', '_'))


def update():
    """ Update the hotfix with updates committed to master.

    This will merge current develop into the current branch.
    """
    branch = git.current_branch(refresh=True)
    master = conf.get('git.master_branch', 'master')

    common.assert_branch_type('feature')
    common.git_checkout(master)
    common.git_pull(master)
    common.git_checkout(branch.name)
    common.git_merge(branch.name, master)


def finish():
    """ Merge current feature into develop. """
    if git.staged() or git.unstaged():
        log.err("You have uncommitted changes in your repo!")
        sys.exit(1)

    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('hotfix')

    # Merge hotfix into master
    common.git_checkout(master)
    common.git_pull(master)
    common.git_merge(master, branch.name)

    # Merge hotfix into develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(master)


def merged():
    """ Cleanup a remotely merged branch. """
    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('hotfix')

    # Pull master with the merged hotfix
    common.git_checkout(master)
    common.git_pull(master)

    # Merge to develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(master)
