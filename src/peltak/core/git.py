# -*- coding: utf-8 -*-
""" Git helpers. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from collections import namedtuple

# local imports
from . import conf
from . import shell


Author = namedtuple('Author', 'name email')


def current_branch():
    """ Return the name of the currently checked out git branch. """
    cmd = 'git symbolic-ref --short HEAD'
    return shell.run(cmd, capture=True).stdout.strip()


def is_dirty(path='.'):
    """ Return **True** if there are any changes/unstaged files. """

    with conf.within_proj_dir(path, quiet=True):
        status = shell.run('git status --porcelain', capture=True).stdout
        return bool(status.strip())


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


def untracked():
    """ Return a list of untracked files in the project repository.

    :return List[str]:
        The list of files not tracked by project git repo.
    """
    with conf.within_proj_dir(quiet=True):
        status = shell.run('git status --porcelain', capture=True).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status.startswith('?? '):
                results.append(file_status[3:].strip())

        return results


def staged():
    """ Return a list of project files staged for commit.

    :return List[str]:
        The list of project files staged for commit.
    """
    with conf.within_proj_dir(quiet=True):
        status = shell.run('git status --porcelain', capture=True).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status and file_status[0] in ('A', 'M'):
                results.append(file_status[3:].strip())

        return results


def ignore():
    """ Return a list of patterns in the project .gitignore

    :return List[str]:
        List of patterns set to be ignored by git.
    """
    with conf.within_proj_dir(quiet=True):
        with open('.gitignore') as fp:
            return [
                l.split('#', 1)[0] for l in fp.readlines() if l.strip()
            ]
