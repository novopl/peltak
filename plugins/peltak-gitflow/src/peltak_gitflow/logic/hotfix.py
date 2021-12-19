# Copyright 2017-2020 Mateusz Klos
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
""" git flow hotfix commands implementation. """
import sys

from peltak.core import conf, context, git, hooks, log

from . import common


def start(name: str) -> None:
    """ Start working on a new hotfix.

    This will create a new branch off master called hotfix/<name>.

    Args:
        name (str):
            The name of the new feature.
    """
    hotfix_branch = 'hotfix/' + common.to_branch_name(name)
    master = conf.get('git.master_branch', 'master')

    common.assert_on_branch(master)

    hooks.register.call('pre-hotfix-start', name)
    common.git_checkout(hotfix_branch, create=True)
    hooks.register.call('post-hotfix-start', name)


def rename(name: str) -> None:
    """ Give the currently developed feature a new name.

    Args:
        name (str):
            The new name of the current feature. The current branch will be
            renamed to 'feature/<new_name>'.
    """
    common.assert_branch_type('hotfix')
    common.git_branch_rename('hotfix/' + name.strip().replace(' ', '_'))


def update() -> None:
    """ Update the hotfix with updates committed to master.

    This will merge current develop into the current branch.
    """
    branch = git.current_branch(refresh=True)
    master = conf.get('git.master_branch', 'master')

    common.assert_branch_type('hotfix')
    common.git_checkout(master)
    common.git_pull(master)
    common.git_checkout(branch.name)
    common.git_merge(branch.name, master)


def finish(fast_forward: bool) -> None:
    """ Merge current feature into develop. """
    pretend = context.get('pretend', False)

    if not pretend and (git.staged() or git.unstaged()):
        log.err(
            "You have uncommitted changes in your repo!\n"
            "You need to stash them before you merge the hotfix branch"
        )
        sys.exit(1)

    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('hotfix')

    hooks.register.call('pre-hotfix-finish', branch)

    # Merge hotfix into master
    common.git_checkout(master)
    common.git_pull(master)
    common.git_merge(master, branch.name, no_ff=not fast_forward)

    # Merge hotfix into develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name, no_ff=not fast_forward)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(master)

    hooks.register.call('post-hotfix-finish', branch)


def merged() -> None:
    """ Cleanup a remotely merged branch. """
    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('hotfix')

    hooks.register.call('pre-hotfix-merged', branch)

    # Pull master with the merged hotfix
    common.git_checkout(master)
    common.git_pull(master)

    # Merge to develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(master)

    hooks.register.call('post-hotfix-merged', branch)
