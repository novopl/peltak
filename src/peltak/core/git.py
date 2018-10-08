# -*- coding: utf-8 -*-
""" Git helpers. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from collections import namedtuple

# 3rd party imports
from six import string_types

# local imports
from . import conf
from . import shell
from . import util


Author = namedtuple('Author', 'name email')
BranchDetails = namedtuple('BranchDetails', 'type title name')
CommitDetails = namedtuple('CommitDetails', 'id author title desc number')


@util.cached_result()
def current_branch():
    """

    :return BranchDetails:
    """
    cmd = 'git symbolic-ref --short HEAD'
    branch_name = shell.run(cmd, capture=True).stdout.strip()

    if '/' in branch_name:
        branch_type, branch_title = branch_name.rsplit('/', 1)
        return BranchDetails(branch_type, branch_title, branch_name)

    return BranchDetails(branch_name, None, branch_name)


@util.cached_result()
def latest_commit():
    """ Return details for the latest commit.

    :return CommitDetails:
        The `CommitDetails` instance for the latest commit on the current
        branch.
    """
    return commit_details()


def commit_details(sha1=''):
    """ Return details about a given commit.

    :param str sha1:
        The sha1 of the commit to query. If not given, it will return the
        details for the latest commit.
    :return CommitDetails:
        A named tuple ``(name, email)`` with the commit author details.
    """
    with conf.within_proj_dir():
        cmd = 'git show -s --format="%h||%an||%ae||%s||%b" {}'.format(sha1)
        result = shell.run(cmd, capture=True).stdout
        commit_id, name, email, title, desc = result.split('||')
        commit_nr = num_commits(refresh=True)
        author = Author(name, email)

        return CommitDetails(commit_id, author, title, desc, commit_nr)


def commit_author(sha1=''):
    """ Return the author of the given commit.

    :param str sha1:
        The sha1 of the commit to query. If not given, it will return the sha1
        for the current commit.
    :return Author:
        A named tuple ``(name, email)`` with the commit author details.
    """
    with conf.within_proj_dir():
        cmd = 'git show -s --format="%an||%ae" {}'.format(sha1)
        result = shell.run(cmd, capture=True).stdout
        name, email = result.split('||')
        return Author(name, email)


@util.cached_result()
def untracked():
    """ Return a list of untracked files in the project repository.

    :return List[str]:
        The list of files not tracked by project git repo.
    """
    with conf.within_proj_dir():
        status = shell.run('git status --porcelain', capture=True).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status.startswith('?? '):
                results.append(file_status[3:].strip())

        return results


@util.cached_result()
def staged():
    """ Return a list of project files staged for commit.

    :return List[str]:
        The list of project files staged for commit.
    """
    with conf.within_proj_dir():
        status = shell.run('git status --porcelain', capture=True).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status and file_status[0] in ('A', 'M', 'D'):
                results.append(file_status[3:].strip())

        return results


@util.cached_result()
def ignore():
    """ Return a list of patterns in the project .gitignore

    :return List[str]:
        List of patterns set to be ignored by git.
    """

    def parse_line(line):   # pylint: disable=missing-docstring
        # Decode if necessary
        if not isinstance(line, string_types):
            line = line.decode('utf-8')

        # Strip comment
        line = line.split('#', 1)[0].strip()

        return line

    ignore_files = [
        conf.proj_path('.gitignore'),
        conf.proj_path('.git/info/exclude'),
        config().get('core.excludesfile')
    ]

    result = []
    for ignore_file in ignore_files:
        if not (ignore_file and os.path.exists(ignore_file)):
            continue

        with open(ignore_file) as fp:
            parsed = (parse_line(l) for l in fp.readlines())
            result += [x for x in parsed if x]

    return result


@util.cached_result()
def num_commits():
    """ Return the number of commits from beginning till current.

    This function will basically count the number of commits in the history
    from the current commit perspective (ignores all other branches).

    :return int:
        Number of commits in the repo from beginning till current commit.
    """
    out = shell.run('git log --oneline', capture=True).stdout.strip()
    return len(out.splitlines())


@util.cached_result()
def config():
    """ Return the current git configuration.

    :return dict:
        The current git config taken from ``git config --list``.
    """
    out = shell.run('git config --list', capture=True).stdout.strip()

    result = {}
    for line in out.splitlines():
        name, value = line.split('=', 1)
        result[name.strip()] = value.strip()

    return result


def verify_branch(branch_name):
    """ Verify if the given branch exists.

    :param str branch_name:
        The name of the branch to check.
    :return bool:
        **True** if a branch with name *branch_name* exits, **False** otherwise.
    """
    try:
        shell.run('git rev-parse --verify {}'.format(branch_name))
        return True
    except IOError:
        return False


@util.cached_result()
def protected_branches():
    """ Return branches protected by deletion.

    By default those are master and devel branches as configured in pelconf.

    :return List[str]:
        Names of important branches that should not be deleted.
    """
    master = conf.get('git.master_branch', 'master')
    develop = conf.get('git.devel_branch', 'develop')
    return conf.get('git.protected_branches', (master, develop))
