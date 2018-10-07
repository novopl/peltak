# -*- coding: utf-8 -*-
""" Helper function to ease implementation of all git flow commands. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# local imports
from peltak.core import git
from peltak.core import log
from peltak.core import shell


def assert_branch_type(branch_type):
    """ Print error and exit if the current branch is not of a given type.

    :param str branch_type:
        The branch type. This assumes the branch is in the '<type>/<title>`
        format.
    """
    branch = git.current_branch(refresh=True)

    if branch.type != branch_type:
        log.err("Not on a <33>{}<31> branch!", branch_type)
        fmt = ("The branch must follow <33>hotfix/<name><31> format and your "
               "branch is is called <33>{}<31>.")
        log.err(fmt, branch.name)
        sys.exit(1)


def assert_on_branch(branch_name):
    """ Print error and exit if *branch_name* is not the current branch.

    :param str branch_name:
        The supposed name of the current branch.
    """
    branch = git.current_branch(refresh=True)

    if branch.name != branch_name:
        log.err("You're not on a <33>{}<31> branch!", branch_name)
        sys.exit(1)


def git_branch_delete(branch_name):
    """ Delete the given brach.

    :param str branch_name:
        Name of the branch to delete.
    """
    if branch_name not in git.protected_branches():
        log.info("Deleting branch <33>{}", branch_name)
        shell.run('git branch -d {}'.format(branch_name))


def git_branch_rename(new_name):
    """ Rename the current branch

    :param str new_name:
        New name for the current branch.
    """
    curr_name = git.current_branch(refresh=True).name()

    if curr_name not in git.protected_branches():
        log.info("Renaming branch from <33>{}<32> to <33>{}".format(
            curr_name, new_name
        ))
        shell.run('git branch -m {}'.format(new_name))


def git_checkout(branch_name, create=False):
    """ Checkout or create a given branch

    :param str branch_name:
        The name of the branch to checkout or create.
    :param bool create:
        If set to **True** it will create the branch instead of checking it out.
    """
    log.info("Checking out <33>{}".format(branch_name))
    shell.run('git checkout {} {}'.format('-b' if create else '', branch_name))


def git_pull(branch_name):
    """ Pull from remote branch.

    :param str branch_name:
        The remote branch to pull.
    """
    log.info("Pulling latest changes on <33>{}", branch_name)
    shell.run('git pull origin {}'.format(branch_name))


def git_merge(base, head, no_ff=False):
    """ Merge *head* into *base*.

    :param str base:
        The base branch. *head* will be merged into this branch.
    :param str head:
        The branch that will be merged into *base*.
    :param bool no_ff:
        If set to **True** it will force git to create merge commit. If set to
        **False** (default) it will do a fast-forward merge if possible.
    """
    branch = git.current_branch(refresh=True)

    if branch.name != base:
        git_checkout(base)

    args = []

    if no_ff:
        args.append('--no-ff')

    log.info("Merging <33>{}<32> into <33>{}<32>", head, base)
    shell.run('git merge {args} {branch}'.format(
        args=' '.join(args),
        branch=head,
    ))

    if branch.name != base:
        git_checkout(branch.name)


def git_prune():
    """ Prune dead branches. """
    log.info("Pruning")
    shell.run('git fetch --prune origin')
