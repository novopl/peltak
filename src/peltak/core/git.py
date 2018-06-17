# -*- coding: utf-8 -*-
"""
Git helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from collections import namedtuple
from os.path import join, exists

# 3rd party imports

# local imports
from . import conf


Author = namedtuple('Author', 'name email')


def current_branch():
    """ Return the name of the currently checked out git branch. """
    return conf.run('git symbolic-ref --short HEAD', capture=True).stdout


def is_dirty(path='.'):
    """ Return **True** if there are any changes/unstaged files. """

    with conf.within_proj_dir(path, quiet=True):
        status = conf.run('git status --porcelain', capture=True).stdout
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
        result = conf.run(cmd, capture=True).stdout
        name, email = result.split('||')
        return Author(name, email)


def load_gitignore(repo_path):
    gitignore_path = join(repo_path, '.gitignore')

    exclude_patterns = []

    if exists(gitignore_path):
        with open(gitignore_path) as fp:
            for line in fp.readlines():
                line = line.strip()

                if line.startswith('#'):
                    continue

                elif line.startswith('/'):
                    line = line[1:]

                exclude_patterns.append(line)

    return exclude_patterns


