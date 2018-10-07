# -*- coding: utf-8 -*-
""" git flow hotfix commands implementation. """
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.core import git
from . import common


def start(name):
    """ Start working on a new hotfix.

    This will create a new branch off master called hotfix/<name>.

    :param str name:
        The name of the new feature.
    """
    branch_name = 'hotfix/' + name.strip().replace(' ', '_')
    common.git_checkout(branch_name, create=True)


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
    branch = git.current_branch()
    master = conf.get('git.master_branch', 'master')

    common.assert_branch_type('feature')
    common.git_checkout(master)
    common.git_pull(master)
    common.git_checkout(branch.name)
    common.git_merge(branch.name, master)


def finish():
    """ Merge current feature into develop. """
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch()

    common.assert_branch_type('hotfix')
    common.git_checkout(master)
    common.git_pull(master)
    common.git_merge(master, branch.name)
    common.git_branch_delete(branch.name)
    common.git_prune()
    common.git_checkout(master)


def merged():
    """ Cleanup a remotely merged branch. """
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch()

    common.assert_branch_type('hotfix')
    common.git_checkout(master)
    common.git_pull(master)
    common.git_branch_delete(branch.name)
    common.git_prune()
    common.git_checkout(master)
