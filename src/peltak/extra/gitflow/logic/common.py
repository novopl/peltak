# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" Helper function to ease implementation of all git flow commands. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import re
import sys
from typing import List

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import git
from peltak.core import log
from peltak.core import shell


RE_INVALID_CHARS = re.compile('[\-\[\]\s(),.]+')


def assert_branch_type(branch_type):
    # type: (str) -> None
    """ Print error and exit if the current branch is not of a given type.

    Args:
        branch_type (str):
            The branch type. This assumes the branch is in the '<type>/<title>`
            format.
    """
    branch = git.current_branch(refresh=True)

    if branch.type != branch_type:
        if context.get('pretend', False):
            log.info("Would assert that you're on a <33>{}/*<32> branch",
                     branch_type)
        else:
            log.err("Not on a <33>{}<31> branch!", branch_type)
            fmt = ("The branch must follow <33>{required_type}/<name><31>"
                   "format and your branch is called <33>{name}<31>.")
            log.err(fmt, required_type=branch_type, name=branch.name)
            sys.exit(1)


def assert_on_branch(branch_name):
    # type: (str) -> None
    """ Print error and exit if *branch_name* is not the current branch.

    Args:
        branch_name (str):
            The supposed name of the current branch.
    """
    branch = git.current_branch(refresh=True)

    if branch.name != branch_name:
        if context.get('pretend', False):
            log.info("Would assert that you're on a <33>{}<32> branch",
                     branch_name)
        else:
            log.err("You're not on a <33>{}<31> branch!", branch_name)
            sys.exit(1)


def git_branch_delete(branch_name):
    # type: (str) -> None
    """ Delete the given branch.

    Args:
        branch_name (str):
            Name of the branch to delete.
    """
    if branch_name not in git.protected_branches():
        log.info("Deleting branch <33>{}", branch_name)
        shell.run('git branch -d {}'.format(branch_name))


def git_branch_rename(new_name):
    # type: (str) -> None
    """ Rename the current branch

    Args:
        new_name (str):
            New name for the current branch.
    """
    curr_name = git.current_branch(refresh=True).name

    if curr_name not in git.protected_branches():
        log.info("Renaming branch from <33>{}<32> to <33>{}".format(
            curr_name, new_name
        ))
        shell.run('git branch -m {}'.format(new_name))


def git_checkout(branch_name, create=False):
    # type: (str, bool) -> None
    """ Checkout or create a given branch

    Args:
        branch_name (str):
            The name of the branch to checkout or create.
        create (bool):
            If set to **True** it will create the branch instead of checking it
            out.
    """
    log.info("Checking out <33>{}".format(branch_name))
    shell.run('git checkout {} {}'.format('-b' if create else '', branch_name))


def git_pull(branch_name):
    # type: (str) -> None
    """ Pull from remote branch.

    Args:
        branch_name (str):
            The remote branch to pull.
    """
    log.info("Pulling latest changes on <33>{}", branch_name)
    shell.run('git pull origin {}'.format(branch_name))


def git_merge(base, head, no_ff=False):
    # type: (str, str, bool) -> None
    """ Merge *head* into *base*.

    Args:
        base (str):
            The base branch. *head* will be merged into this branch.
        head (str):
            The branch that will be merged into *base*.
        no_ff (bool):
            If set to **True** it will force git to create merge commit. If set
            to **False** (default) it will do a fast-forward merge if possible.
    """
    pretend = context.get('pretend', False)
    branch = git.current_branch(refresh=True)

    if branch.name != base and not pretend:
        git_checkout(base)

    args = []

    if no_ff:
        args.append('--no-ff')

    log.info("Merging <33>{}<32> into <33>{}<32>", head, base)
    shell.run('git merge {args} {branch}'.format(
        args=' '.join(args),
        branch=head,
    ))

    if branch.name != base and not pretend:
        git_checkout(branch.name)


def git_prune():
    # type: () -> None
    """ Prune dead branches. """
    log.info("Pruning")
    shell.run('git fetch --prune origin')


def get_base_branch():
    # type: () -> str
    """ Return the base branch for the current branch.

    This function will first try to guess the base branch and if it can't it
    will let the user choose the branch from the list of all local branches.

    Returns:
        str: The name of the branch the current branch is based on.
    """
    base_branch = git.guess_base_branch()

    if base_branch is None:
        log.info("Can't guess the base branch, you have to pick one yourself:")
        base_branch = choose_branch()

    return base_branch


def choose_branch(exclude=None):
    # type: (List[str]) -> str
    """ Show the user a menu to pick a branch from the existing ones.

    Args:
        exclude (list[str]):
            List of branch names to exclude from the menu. By default it will
            exclude master and develop branches. To show all branches pass an
            empty array here.

    Returns:
        str: The name of the branch chosen by the user. If the user inputs an
        invalid choice, he will be asked again (and again) until he picks a
        a valid branch.
    """
    if exclude is None:
        master = conf.get('git.master_branch', 'master')
        develop = conf.get('git.devel_branch', 'develop')
        exclude = {master, develop}

    branches = list(set(git.branches()) - exclude)

    # Print the menu
    for i, branch_name in enumerate(branches):
        shell.cprint('<90>[{}] <33>{}'.format(i + 1, branch_name))

    # Get a valid choice from the user
    choice = 0
    while choice < 1 or choice > len(branches):
        prompt = "Pick a base branch from the above [1-{}]".format(
            len(branches)
        )
        choice = click.prompt(prompt, value_proc=int)
        if not (1 <= choice <= len(branches)):
            fmt = "Invalid choice {}, you must pick a number between {} and {}"
            log.err(fmt.format(choice, 1, len(branches)))

    return branches[choice - 1]


def to_branch_name(name):
    # type: (str) -> str
    """ Convert a given name into a valid branch name.

    This is helpful to sanitize user input before creating a new branch.

    Args:
        name (str):
            The name of the branch as provided by the user.

    Returns:
        str: The name mangled where all special characters and spaces are
        replaced by underscores.
    """
    return RE_INVALID_CHARS.sub(' ', name).strip().replace(' ', '_').lower()


# Used in docstrings only until we drop python2 support
del List
