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
    from .impl import git

    git.add_hooks()


@git_cli.command('push')
def push():
    """ Push the current branch and set to track remote.

    Example::

        $ peltak git push

    """
    from .impl import git

    git.push()


@git_cli.command('merged')
@click.argument('target', required=False)
def merged(target=None):
    """ Checkout the target branch, pull and delete the merged branch.

    This is to ease the repetitive cleanup of each merged branch.

    Example Config (those the are defaults)::

        \b
        conf.init({
            'main_branch': 'develop',
            'master_branch': 'master',
            'protected_branches': ['master', 'develop'],
            'release_branch_pattern: 'release/*'
        })

    Example::

        $ peltak git merged develop # Branch was merged to develop
        $ peltak git merged master  # Branch was merged to master
        $ peltak git merged         # Autodetect where the branch was merged

    """
    from .impl import git

    git.merged(target)
