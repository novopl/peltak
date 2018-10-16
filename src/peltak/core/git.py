# -*- coding: utf-8 -*-
""" Git helpers. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from collections import namedtuple

# 3rd party imports
import attr
from six import string_types

# local imports
from . import conf
from . import shell
from . import util


Author = namedtuple('Author', 'name email')
BranchDetails = namedtuple('BranchDetails', 'type title name')


@attr.s
class BranchDetails(object):
    """ Branch name parsed into type and title.

    Helpful for things like implementing git flow etc.
    """
    name = attr.ib(type=str)
    type = attr.ib(type=str, default=None)
    title = attr.ib(type=str, default=None)

    @classmethod
    def parse(cls, branch_name):
        """ Parse branch name into BranchDetails instance.

        :param str branch_name:
            The name of the branch to parse.
        :return BranchDetails:
            The parsed branch name - easy to query.
        """
        if '/' in branch_name:
            branch_type, branch_title = branch_name.rsplit('/', 1)
            return BranchDetails(branch_name, branch_type, branch_title)
        else:
            return BranchDetails(branch_name, None, branch_name)


class CommitDetails(object):
    """ Allows querying git commits for details. """
    def __init__(self, sha1, author, title, desc, parents_sha1):
        self.id = sha1[:7]
        self.sha1 = sha1
        self.author = author
        self.title = title
        self.desc = desc
        self.parents_sha1 = parents_sha1
        self._branches = None
        self._parents = None

    @property
    def branches(self):
        """ Return all branches this commit is on.

        :return List[str]:
            List of branches this commit belongs to.
        """
        if self._branches is None:
            cmd = 'git branch --contains {}'.format(self.sha1)
            out = shell.run(cmd, capture=True).stdout.strip()
            self._branches = [x.strip('* \t\n') for x in out.splitlines()]

        return self._branches

    @property
    def parents(self):
        """ Return parents of the this commit.

        :return List[CommitDetails]:
            The parents of the current commit.
        """
        if self._parents is None:
            self._parents = [CommitDetails.get(x) for x in self.parents_sha1]

        return self._parents

    @property
    def number(self):
        """ Return this commits number.

        This is the same as the total number of commits in history up until
        this commit.

        This value can be useful in some CI scenarios as it allows to track
        progress on any given branch (although there can be two commits with the
        same number existing on different branches).

        :return int:
            The commit number/index.
        """
        cmd = 'git log --oneline {}'.format(self.sha1)
        out = shell.run(cmd, capture=True).stdout.strip()
        return len(out.splitlines())

    @classmethod
    def get(cls, sha1=''):
        """ Return details about a given commit.

        :param str sha1:
            The sha1 of the commit to query. If not given, it will return the
            details for the latest commit.
        :return CommitDetails:
            Commit details. You can use the instance of the class to query
            git tree further.
        """
        with conf.within_proj_dir():
            cmd = 'git show -s --format="%H||%an||%ae||%s||%b||%P" {}'.format(
                sha1
            )
            result = shell.run(cmd, capture=True).stdout

        sha1, name, email, title, desc, parents = result.split('||')

        return CommitDetails(
            sha1=sha1,
            author=Author(name, email),
            title=title,
            desc=desc,
            parents_sha1=parents.split(),
        )


@util.cached_result()
def current_branch():
    """ Return the BranchDetails for the current branch.

    :return BranchDetails:
        The details of the current branch.
    """
    cmd = 'git symbolic-ref --short HEAD'
    branch_name = shell.run(cmd, capture=True).stdout.strip()

    return BranchDetails.parse(branch_name)


@util.cached_result()
def latest_commit():
    """ Return details for the latest commit.

    :return CommitDetails:
        The `CommitDetails` instance for the latest commit on the current
        branch.
    """
    return CommitDetails.get()


def commit_details(sha1=''):
    """ Return details about a given commit.

    :param str sha1:
        The sha1 of the commit to query. If not given, it will return the
        details for the latest commit.
    :return CommitDetails:
        A named tuple ``(name, email)`` with the commit author details.
    """
    return CommitDetails.get(sha1)


def commit_branches(sha1):
    """ Get the name of the branches that this commit belongs to. """
    cmd = 'git branch --contains {}'.format(sha1)
    return shell.run(cmd, capture=True).stdout.strip().split()


@util.cached_result()
def guess_base_branch():
    """ Try to guess the base branch for the current branch.

    Do not trust this guess. git makes it pretty much impossible to guess
    the base branch reliably so this function implements few heuristics that
    will work on most common use cases but anything a bit crazy will probably
    trip this function.

    :return Optional[str]:
        The name of the base branch for the current branch or **None** if
        it can't be guessed.
    """
    my_branch = current_branch(refresh=True).name

    curr = latest_commit()
    if len(curr.branches) > 1:
        # We're possibly at the beginning of the new branch (currently both
        # on base and new branch).
        other = [x for x in curr.branches if x != my_branch]
        if len(other) == 1:
            return other[0]
        return None
    else:
        # We're on one branch
        parent = curr

        while parent and my_branch in parent.branches:
            curr = parent

            if len(curr.branches) > 1:
                other = [x for x in curr.branches if x != my_branch]
                if len(other) == 1:
                    return other[0]
                return None

            parents = [p for p in curr.parents if my_branch in p.branches]
            num_parents = len(parents)

            if num_parents > 2:
                # More than two parent, give up
                return None
            if num_parents == 2:
                # This is a merge commit.
                for p in parents:
                    if p.branches == [my_branch]:
                        parent = p
                        break
            elif num_parents == 1:
                parent = parents[0]
            elif num_parents == 0:
                parent = None

        return None


@util.mark_deprecated('CommitDetails.get().author')
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
def unstaged():
    """ Return a list of unstaged files in the project repository.

    :return List[str]:
        The list of files not tracked by project git repo.
    """
    with conf.within_proj_dir():
        status = shell.run('git status --porcelain', capture=True).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status.strip() and file_status[0] == ' ':
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
def branches():
    """ Return a list of branches in the current repo.

    :return List[str]:
        A list of branches in the current repo.
    """
    out = shell.run('git branch', capture=True).stdout.strip()
    return [x.strip('* \t\n') for x in out.splitlines()]


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
