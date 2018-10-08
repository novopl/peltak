# -*- coding: utf-8 -*-
""" git flow feature commands implementation. """
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.core import git
from . import common


def start(name):
    """ Start working on a new feature by branching off develop.

    This will create a new branch off develop called feature/<name>.

    :param str name:
        The name of the new feature.
    """
    branch_name = 'feature/' + name.strip().replace(' ', '_')
    common.git_checkout(branch_name, create=True)


def update():
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
    """ Give the currently developed feature a new name.

    :param str name:
        The new name of the current feature. The current branch will be
        renamed to 'feature/<new_name>'.
    """
    common.assert_branch_type('feature')
    common.git_branch_rename('feature/' + name.strip().replace(' ', '_'))


def finish():
    """ Merge current feature branch into develop. """
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
    """ Cleanup a remotely merged branch. """
    develop = conf.get('git.devel_branch', 'develop')
    branch_name = git.current_branch(refresh=True).name()

    common.assert_branch_type('feature')

    # Pull master with the merged hotfix
    common.git_checkout(develop)
    common.git_pull(develop)

    # Cleanup
    common.git_branch_delete(branch_name)
    common.git_prune()

    common.git_checkout(develop)
