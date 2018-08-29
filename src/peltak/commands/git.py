# -*- coding: utf-8 -*-
""" git helpers. """
from __future__ import absolute_import
from . import cli, click


@cli.group('git')
def git_cli():
    """ Git related commands """
    pass


@git_cli.command('add-hooks')
def add_hooks():
    """ Setup project git hooks.

    This will run all the checks before pushing to avoid waiting for the CI
    fail.

    Example::

        $ peltak git add-hooks
    """
    import os
    from peltak.core import conf
    from peltak.core import log

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
            'source "$REPO_PATH/env/bin/activate"',
            '',
            'peltak lint --commit',
        ]))
        fp.write('\n')

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
            'peltak test --allow-empty',
        ]))
        fp.write('\n')

    log.info("Making hooks executable")
    os.chmod(conf.proj_path('.git/hooks/pre-commit'), 0o755)
    os.chmod(conf.proj_path('.git/hooks/pre-push'), 0o755)


@git_cli.command('push')
def push():
    """ Push the current branch and set to track remote.

    Example::

        $ peltak git push

    """
    from peltak.core import git
    from peltak.core import shell

    branch = git.current_branch()
    shell.run('git push -u origin {}'.format(branch))


@git_cli.command('merged')
@click.argument('target', required=False)
def merged(target=None):
    """ Checkout the target branch, pull and delete the merged branch.

    This is to ease the repetitive cleanup of each merged branch.

    Example Config (those the are defaults)::

        \b
        conf.init({
            'MAIN_BRANCH': 'develop',
            'MASTER_BRANCH': 'master',
            'PROTECTED_BRANCHES': ['master', 'develop'],
            'RELEASE_BRANCH_PATTERN: 'release/*'
        })

    Example::

        $ peltak git merged develop # Branch was merged to develop
        $ peltak git merged master  # Branch was merged to master
        $ peltak git merged         # Autodetect where the branch was merged

    """
    from fnmatch import fnmatch
    from peltak.core import conf
    from peltak.core import git
    from peltak.core import log
    from peltak.core import shell

    main_branch = conf.get('MAIN_BRANCH', 'develop')
    master_branch = conf.get('MASTER_BRANCH', 'master')
    protected_branches = conf.get('PROTECTED_BRANCHES', ('master', 'develop'))
    release_branch_pattern = conf.get('RELEASE_BRANCH_PATTERN', 'release/*')
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
