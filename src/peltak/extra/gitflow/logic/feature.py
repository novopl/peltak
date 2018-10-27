# -*- coding: utf-8 -*-
""" git flow feature commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# local imports
from peltak.core import conf
from peltak.core import git
from peltak.core import log
from . import common


def start(name):
    # type: (str) -> None
    """ Start working on a new feature by branching off develop.

    This will create a new branch off develop called feature/<name>.

    Args:
        name (str):
            The name of the new feature.
    """
    feature_name = 'feature/' + common.to_branch_name(name)
    develop = conf.get('git.devel_branch', 'develop')

    common.assert_on_branch(develop)
    common.git_checkout(feature_name, create=True)


def update():
    # type: () -> None
    """ Update the feature with updates committed to develop.

    This will merge current develop into the current branch.
    """
    branch = git.current_branch(refresh=True)
    develop = conf.get('git.devel_branch', 'develop')

    common.assert_branch_type('feature')
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_checkout(branch.name)
    common.git_merge(branch.name, develop)


def rename(name):
    # type: (str) -> None
    """ Give the currently developed feature a new name.

    Args:
        name (str):
            The new name of the current feature. The current branch will be
            renamed to 'feature/<new_name>'.
    """
    common.assert_branch_type('feature')
    common.git_branch_rename('feature/' + name.strip().replace(' ', '_'))


def finish():
    # type: () -> None
    """ Merge current feature branch into develop. """
    if git.staged() or git.unstaged():
        log.err(
            "You have uncommitted changes in your repo!\n"
            "You need to stash them before you merge the feature branch"
        )
        sys.exit(1)

    develop = conf.get('git.devel_branch', 'develop')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('feature')

    # Merge feature into develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(develop)


def merged():
    # type: () -> None
    """ Cleanup a remotely merged branch. """
    develop = conf.get('git.devel_branch', 'develop')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('feature')

    # Pull develop with the merged feature
    common.git_checkout(develop)
    common.git_pull(develop)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(develop)
