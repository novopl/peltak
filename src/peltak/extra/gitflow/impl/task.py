# -*- coding: utf-8 -*-
""" git flow feature commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# 3rd party imports
import click

# local imports
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from . import common


def start(name):
    """ Start working on a new feature by branching off develop.

    This will create a new branch off develop called feature/<name>.

    :param str name:
        The name of the new feature.
    """
    branch = git.current_branch(refresh=True)
    task_branch = 'task/' + common.to_branch_name(name)

    if branch.type not in ('feature', 'hotfix'):
        log.err("Task branches can only branch off <33>feature<32> or "
                "<33>hotfix<32> branches")
        sys.exit(1)

    common.git_checkout(task_branch, create=True)


def update():
    """ Update the feature with updates committed to develop.

    This will merge current develop into the current branch.
    """
    branch = git.current_branch(refresh=True)
    base_branch = common.get_base_branch()

    common.assert_branch_type('task')
    common.git_checkout(base_branch)
    common.git_pull(base_branch)
    common.git_checkout(branch.name)
    common.git_merge(branch.name, base_branch)


def rename(name):
    """ Give the currently developed feature a new name.

    :param str name:
        The new name of the current feature. The current branch will be
        renamed to 'feature/<new_name>'.
    """
    common.assert_branch_type('task')
    common.git_branch_rename('task/' + name.strip().replace(' ', '_'))


def finish():
    """ Merge current feature branch into develop. """
    if git.staged() or git.unstaged():
        log.err("You have uncommitted changes in your repo!")
        sys.exit(1)

    branch = git.current_branch(refresh=True)
    base = common.get_base_branch()

    prompt = "<32>Merge <33>{}<32> into <33>{}<0>?".format(branch.name, base)
    if not click.confirm(shell.fmt(prompt)):
        log.info("Cancelled")
        return

    common.assert_branch_type('task')

    # Merge task into it's base feature branch
    common.git_checkout(base)
    common.git_pull(base)
    common.git_merge(base, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(base)


def merged():
    """ Cleanup a remotely merged branch. """
    base_branch = common.get_base_branch()
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('task')

    # Pull feature branch with the merged task
    common.git_checkout(base_branch)
    common.git_pull(base_branch)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(base_branch)
