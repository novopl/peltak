# -*- coding: utf-8 -*-
""" git helpers. """
from __future__ import absolute_import
from . import root_cli


@root_cli.group('git')
def git_cli():
    # type: () -> None
    """ Git related commands """
    pass


@git_cli.command('add-hooks')
def add_hooks():
    # type: () -> None
    """ Setup project git hooks.

    This will run all the checks before pushing to avoid waiting for the CI
    fail.

    Example::

        $ peltak git add-hooks
    """
    from peltak.commands import git

    git.add_hooks()


@git_cli.command('push')
def push():
    # type: () -> None
    """ Push the current branch and set to track remote.

    Example::

        $ peltak git push

    """
    from peltak.commands import git

    git.push()
