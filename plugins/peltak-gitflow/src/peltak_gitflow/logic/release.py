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
import os
import sys

from peltak.core import conf, context, git, hooks, log, shell, versioning

from . import common


def start(component: str, exact: str) -> None:
    """ Create a new release branch.

    Args:
        component (str):
            Version component to bump when creating the release. Can be *major*,
            *minor* or *patch*.
        exact (str):
            The exact version to set for the release. Overrides the component
            argument. This allows to re-release a version if something went
            wrong with the release upload.
    """
    version_files = versioning.get_version_files()

    develop = conf.get('git.devel_branch', 'develop')
    common.assert_on_branch(develop)

    with conf.within_proj_dir():
        out = shell.run('git status --porcelain', capture=True).stdout
        lines = out.split(os.linesep)
        has_changes = any(
            not line.startswith('??') for line in lines if line.strip()
        )

    if has_changes:
        log.info("Cannot release: there are uncommitted changes")
        exit(1)

    old_ver, new_ver = versioning.bump(component, exact)

    log.info("Bumping package version")
    log.info("  old version: <35>{}".format(old_ver))
    log.info("  new version: <35>{}".format(new_ver))

    with conf.within_proj_dir():
        branch = 'release/' + new_ver

        hooks.register.call('pre-release-start', branch, old_ver, new_ver)

        common.git_checkout(branch, create=True)

        log.info("Creating commit for the release")
        shell.run('git add {files} && git commit -m "{msg}"'.format(
            files=' '.join(f'"{v.path}"' for v in version_files),
            msg="Releasing v{}".format(new_ver)
        ))

        hooks.register.call('post-release-start', branch, old_ver, new_ver)


def finish(fast_forward: bool) -> None:
    """ Merge current release into develop and master and tag it. """
    pretend = context.get('pretend', False)

    if not pretend and (git.staged() or git.unstaged()):
        log.err(
            "You have uncommitted changes in your repo!\n"
            "You need to stash them before you merge the release branch"
        )
        sys.exit(1)

    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('release')

    hooks.register.call('pre-release-finish', branch)

    # Merge release into master
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name, no_ff=not fast_forward)

    # Merge release into develop
    common.git_checkout(master)
    common.git_pull(master)
    common.git_merge(master, branch.name, no_ff=not fast_forward)

    # Tag the release commit with version number
    try:
        # If peltak-changelog is installed, use it for commit message
        from peltak_changelog.logic import changelog  # type: ignore

        tag(changelog())
    except ImportError:
        tag(f"v{versioning.current()}")

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(master)

    hooks.register.call('post-release-finish', branch)


def merged() -> None:
    """ Cleanup the release branch after it was remotely merged to master. """
    develop = conf.get('git.devel_branch', 'develop')
    master = conf.get('git.master_branch', 'master')
    branch = git.current_branch(refresh=True)

    common.assert_branch_type('release')

    hooks.register.call('pre-release-merged', branch)

    # Pull master with the merged release
    common.git_checkout(master)
    common.git_pull(master)

    # Merge to develop
    common.git_checkout(develop)
    common.git_pull(develop)
    common.git_merge(develop, branch.name)

    # Cleanup
    common.git_branch_delete(branch.name)
    common.git_prune()

    common.git_checkout(develop)
    hooks.register.call('post-release-merged', branch)


def tag(message: str) -> None:
    """ Tag the current commit with the current version. """
    release_ver = versioning.current()
    message = message or 'v{} release'.format(release_ver)

    with conf.within_proj_dir():
        log.info("Creating release tag")
        git.tag(
            author=git.latest_commit().author,
            name='v{}'.format(release_ver),
            message=message,
        )
