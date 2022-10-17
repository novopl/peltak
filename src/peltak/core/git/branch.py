from typing import List, Optional

from .. import conf, shell, util
from .types import BranchDetails, CommitDetails


@util.cached_result()
def current_branch() -> BranchDetails:
    """ Return the BranchDetails for the current branch.

    Return:
        BranchDetails: The details of the current branch.
    """
    cmd = 'git symbolic-ref --short HEAD'
    branch_name = shell.run(
        cmd,
        capture=True,
        never_pretend=True
    ).stdout.strip()

    return BranchDetails.parse(branch_name)


@util.cached_result()
def latest_commit() -> CommitDetails:
    """ Return details for the latest commit.

    Returns:
        CommitDetails: The `CommitDetails` instance for the latest commit on the
        current branch.
    """
    return CommitDetails.get()


def commit_details(sha1: str = '') -> CommitDetails:
    """ Return details about a given commit.

    Args:
        sha1 (str):
            The sha1 of the commit to query. If not given, it will return the
            details for the latest commit.

    Returns:
        CommitDetails: A named tuple ``(name, email)`` with the commit author
        details.
    """
    return CommitDetails.get(sha1)


def commit_branches(sha1: str) -> List[str]:
    """ Get the name of the branches that this commit belongs to. """
    cmd = 'git branch --contains {}'.format(sha1)
    return shell.run(
        cmd,
        capture=True,
        never_pretend=True
    ).stdout.strip().split()


@util.cached_result()
def guess_base_branch() -> Optional[str]:
    """ Try to guess the base branch for the current branch.

    Do not trust this guess. git makes it pretty much impossible to guess
    the base branch reliably so this function implements few heuristics that
    will work on most common use cases but anything a bit crazy will probably
    trip this function.

    Returns:
        Optional[str]: The name of the base branch for the current branch if
        guessable or **None** if can't guess.
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


@util.cached_result()
def branches() -> List[str]:
    """ Return a list of branches in the current repo.

    Returns:
        list[str]: A list of branches in the current repo.
    """
    out = shell.run(
        'git branch',
        capture=True,
        never_pretend=True
    ).stdout.strip()
    return [x.strip('* \t\n') for x in out.splitlines()]


def verify_branch(branch_name: str) -> bool:
    """ Verify if the given branch exists.

    Args:
        branch_name (str):
            The name of the branch to check.

    Returns:
        bool: **True** if a branch with name *branch_name* exits, **False**
        otherwise.
    """
    try:
        shell.run(
            'git rev-parse --verify {}'.format(branch_name),
            never_pretend=True
        )
        return True
    except IOError:
        return False


@util.cached_result()
def protected_branches() -> List[str]:
    """ Return branches protected by deletion.

    By default those are master and devel branches as configured in pelconf.

    Returns:
        list[str]: Names of important branches that should not be deleted.
    """
    master = conf.get('git.master_branch', 'master')
    develop = conf.get('git.devel_branch', 'develop')
    return conf.get('git.protected_branches', (master, develop))
