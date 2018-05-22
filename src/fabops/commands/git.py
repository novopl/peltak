# -*- coding: utf-8 -*-
"""
git helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os

# 3rd party imports
from fabric.api import local

# local imports
from .common import conf
from .common import git
from .common import log


def addgithooks():
    """ Setup project git hooks.

    This will run all the checks before pushing to avoid waiting for the CI
    fail.
    """
    log.info("Adding pre-commit hook")
    with open(conf.proj_path('.git/hooks/pre-commit'), 'w') as fp:
        fp.write('\n'.join([
            '#!/bin/bash',
            'PATH="/opt/local/libexec/gnubin:$PATH"',
            (
                'REPO_PATH=$(dirname "$(dirname "$(dirname '
                '"$(readlink -fm "$0")")")")'
            ),
            '',
            'echo "REPO_PATH=$REPO_PATH"',
            'source "$REPO_PATH/env/bin/activate"',
            '',
            'fab lint',
        ]))

    log.info("Adding pre-push hook")
    with open(conf.proj_path('.git/hooks/pre-push'), 'w') as fp:
        fp.write('\n'.join([
            '#!/bin/bash',
            'PATH="/opt/local/libexec/gnubin:$PATH"',
            (
                'REPO_PATH=$(dirname "$(dirname "$(dirname '
                '"$(readlink -fm "$0")")")")'
            ),
            '',
            'source "$REPO_PATH/env/bin/activate"',
            '',
            'fab test',
        ]))

    log.info("Making hooks executable")
    os.chmod(conf.proj_path('.git/hooks/pre-commit'), 0o755)
    os.chmod(conf.proj_path('.git/hooks/pre-push'), 0o755)


def push():
    """ Push the current branch and set to track remote. """
    branch = git.current_branch()
    local('git push -u origin {}'.format(branch))


def merged(target=None):
    """ Checkout develop, pull and delete merged branches.

    This is to ease the repetitive cleanup of each merged branch.
    """
    protected_branches = ('master', 'develop')
    branch = git.current_branch()

    if target is None:
        target = 'master' if branch.startswith('release/') else 'develop'

    try:
        local('git rev-parse --verify {}'.format(branch))
    except:
        log.err("Branch '{}' does not exist".format(branch))

    log.info("Checking out ^33{}".format(target))
    local('git checkout {}'.format(target))

    log.info("Pulling latest changes")
    local('git pull origin {}'.format(target))

    if branch not in protected_branches:
        log.info("Deleting branch ^33{}".format(branch))
        local('git branch -d {}'.format(branch))

    log.info("Pruning")
    local('git fetch --prune origin')

    log.info("Checking out ^33{}^32 branch".format(target))
    local('git checkout {}'.format(target))
