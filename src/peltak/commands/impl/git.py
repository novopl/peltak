# -*- coding: utf-8 -*-
""" Git commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from fnmatch import fnmatch

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import git
from peltak.core import log
from peltak.core import shell


def add_hooks():
    """ Add git hooks for commit and push to run linting and tests. """

    # Detect virtualenv the hooks should use
    virtual_env = conf.getenv('VIRTUAL_ENV')
    if virtual_env is None:
        log.err("You are not inside a virtualenv")
        confirm_msg = (
            "Are you sure you want to use global python installation "
            "to run your git hooks? [y/N] "
        )
        click.prompt(confirm_msg, default=False)
        if not click.confirm(confirm_msg):
            log.info("Cancelling")
            return

        load_venv = ''
    else:
        load_venv = 'source "{}/bin/activate"'.format(virtual_env)

    # Write pre-commit hook
    commit_hook = conf.proj_path('.git/hooks/pre-commit')
    log.info("Adding pre-commit hook <33>{}", commit_hook)
    with open(commit_hook, 'w') as fp:
        fp.write('\n'.join([
            '#!/bin/bash',
            'PATH="/opt/local/libexec/gnubin:$PATH"',
            '',
            load_venv,
            '',
            'peltak lint --commit',
        ]))
        fp.write('\n')

    # Write pre-push hook
    push_hook = conf.proj_path('.git/hooks/pre-push')
    log.info("Adding pre-push hook: <33>{}", push_hook)
    with open(push_hook, 'w') as fp:
        fp.write('\n'.join([
            '#!/bin/bash',
            'PATH="/opt/local/libexec/gnubin:$PATH"',
            '',
            load_venv,
            '',
            'peltak test --allow-empty',
        ]))
        fp.write('\n')

    log.info("Making hooks executable")
    os.chmod(conf.proj_path('.git/hooks/pre-commit'), 0o755)
    os.chmod(conf.proj_path('.git/hooks/pre-push'), 0o755)


def push():
    """ Push the current branch to origin.

    This is an equivalent of ``git push -u origin <branch>``. Mainly useful for
    the first push as afterwards ``git push`` is just quicker. Free's you from
    having to manually type the current branch name in the first push.
    """
    branch = git.current_branch()
    shell.run('git push -u origin {}'.format(branch))


def merged(target=None):
    """ Cleanup a remotely merged branch. """
    main_branch = conf.get('main_branch', 'develop')
    master_branch = conf.get('master_branch', 'master')
    protected_branches = conf.get('protected_branches', ('master', 'develop'))
    release_branch_pattern = conf.get('release_branch_pattern', 'release/*')
    branch = git.current_branch()

    if target is None:
        if fnmatch(branch, release_branch_pattern):
            target = master_branch
        else:
            target = main_branch

    try:
        shell.run('git rev-parse --verify {}'.format(branch))
    except IOError:
        log.err("Branch '{}' does not exist".format(branch))

    log.info("Checking out <33>{}".format(target))
    shell.run('git checkout {}'.format(target))

    log.info("Pulling latest changes")
    shell.run('git pull origin {}'.format(target))

    if branch not in protected_branches:
        log.info("Deleting branch <33>{}".format(branch))
        shell.run('git branch -d {}'.format(branch))

    log.info("Pruning")
    shell.run('git fetch --prune origin')

    log.info("Checking out <33>{}<32> branch".format(target))
    shell.run('git checkout {}'.format(target))
