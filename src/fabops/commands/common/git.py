# -*- coding: utf-8 -*-
"""
Git helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from collections import namedtuple

# 3rd party imports
from fabric.api import local, quiet

# local imports
from . import project


Author = namedtuple('Author', 'name email')


def current_branch():
    """ Return the name of the currently checked out git branch. """
    with quiet():
        return local('git symbolic-ref --short HEAD', capture=True).stdout


def is_dirty(path='.'):
    """ Return **True** if there are any changes/unstaged files. """

    with project.inside(path, quiet=True):
        status = local('git status --porcelain', capture=True).stdout
        return bool(status.strip())


def commit_author(sha1=''):
    """ Return the author of the given commit.

    :param str sha1:
        The sha1 of the commit to query. If not given, it will return the sha1
        for the current commit.
    :return Author:
        A named tuple ``(name, email)`` with the commit author details.
    """
    with project.inside():
        cmd = 'git show --format="%an||%ae" {}'.format(sha1)
        result = local(cmd, capture=True).stdout
        name, email = result.split('||')
        return Author(name, email)
