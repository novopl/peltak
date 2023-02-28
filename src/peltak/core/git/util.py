# Copyright 2017-2021 Mateusz Klos
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
import os
from typing import Any, Dict, List, Optional

from .. import conf, shell, util
from .branch import latest_commit
from .types import Author


@util.mark_deprecated('CommitDetails.get().author')
def commit_author(sha1: str = '') -> Author:
    """ Return the author of the given commit.

    Args:
        sha1:
            The sha1 of the commit to query. If not given, it will return the
            sha1 for the current commit.
    Returns:
        Author: A named tuple ``(name, email)`` with the commit author details.
    """
    with conf.within_proj_dir():
        cmd = 'git show -s --format="%an||%ae" {}'.format(sha1)
        result = shell.run(
            cmd,
            capture=True,
            never_pretend=True
        ).stdout
        name, email = result.split('||')
        return Author(name, email)


@util.cached_result()
def ignore() -> List[str]:
    """ Return a list of patterns in the project .gitignore

    Returns:
        List of patterns set to be ignored by git.
    """

    def parse_line(line):   # pylint: disable=missing-docstring
        # Decode if necessary
        if not isinstance(line, str):
            line = line.decode('utf-8')

        # Strip comment
        line = line.split('#', 1)[0].strip()

        return line

    ignore_files = [
        conf.proj_path('.gitignore'),
        conf.proj_path('.git/info/exclude'),
        config().get('core.excludesfile')
    ]

    result: List[str] = []
    for ignore_file in ignore_files:
        if not (ignore_file and os.path.exists(ignore_file)):
            continue

        with open(ignore_file) as fp:
            parsed = (parse_line(line) for line in fp.readlines())
            result += [x for x in parsed if x]

    return result


def tag(name: str, message: str, author: Optional[Author] = None):
    """ Tag the current commit.

    Args:
        name:
            The tag name.
        message:
            The tag message. Same as ``-m`` parameter in ``git tag``.
        author:
            The commit author. Will default to the author of the commit.
    """
    cmd = (
        'git -c "user.name={author.name}" -c "user.email={author.email}" '
        'tag -a "{name}" -m "{message}"'
    ).format(
        author=author or latest_commit().author,
        name=name,
        message=message.replace('"', '\\"').replace('`', '\\`'),
    )
    shell.run(cmd)


@util.cached_result()
def config() -> Dict[str, Any]:
    """ Return the current git configuration.

    Returns:
        The current git config taken from ``git config --list``.
    """
    out = shell.run(
        'git config --list',
        capture=True,
        never_pretend=True
    ).stdout.strip()

    result = {}
    for line in out.splitlines():
        name, value = line.split('=', 1)
        result[name.strip()] = value.strip()

    return result


@util.cached_result()
def tags() -> List[str]:
    """ Returns all tags in the repo.

    Returns:
        List of all tags in the repo, sorted as versions.

    All tags returned by this function will be parsed as if the contained
    versions (using ``v:refname`` sorting).
    """
    return shell.run(
        'git tag --sort=v:refname',
        capture=True,
        never_pretend=True
    ).stdout.strip().splitlines()
