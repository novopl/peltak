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
import dataclasses
from collections import namedtuple
from typing import List, Optional

from .. import conf, shell


Author = namedtuple('Author', 'name email')


@dataclasses.dataclass
class BranchDetails:
    """ Branch name parsed into type and title.

    Helpful for things like implementing git flow etc.

    Attributes:
        name (str):
            The full name of the branch as returned by git.
        type (str):
            The type of the branch. This assumes the ``type/title`` branch
            naming format and will be the text before ``/`` in the branch name.
        title (str):
            The title of the branch. This assumes the ``type/title`` branch
            naming format and will be the text after ``/`` in the branch name.
    """
    name: str
    type: Optional[str] = None
    title: Optional[str] = None

    @classmethod
    def parse(cls, branch_name: str) -> 'BranchDetails':
        """ Parse branch name into BranchDetails instance.

        Args:
            branch_name (str):
                The name of the branch to parse.

        Returns:
            BranchDetails: The parsed branch name - easy to use.
        """
        if '/' in branch_name:
            branch_type, branch_title = branch_name.rsplit('/', 1)
            return BranchDetails(branch_name, branch_type, branch_title)
        else:
            return BranchDetails(branch_name, None, branch_name)


@dataclasses.dataclass
class CommitDetails:
    """ Allows querying git commits for details.

    Attributes:
        id (str):
            The commit ID (first 7 characters taken from `sha1`).
        sha1 (str):
            Full SHA1 of the commit.
        author (Author):
            The commit author.
        title (str):
            The title of the commit. This is the first line of the commit
            message and should usually be shorter than 50 characters.
        desc (str):
            The commit description. This is the portion following the title.
            Will be an empty string if the commit contains only the title.
        parents_sha1 (List[str]):
            List of SHA1s of parents of this commit.
    """
    sha1: str
    author: Author
    title: str
    desc: str
    parents_sha1: Optional[str]
    _branches: List[str] = dataclasses.field(default_factory=list)
    _parents: List['CommitDetails'] = dataclasses.field(default_factory=list)

    @property
    def id(self) -> str:
        return self.sha1[:7]

    @property
    def branches(self) -> List[str]:
        """ List of all branches this commit is a part of. """
        if self._branches is None:
            cmd = 'git branch --contains {}'.format(self.sha1)
            out = shell.run(
                cmd,
                capture=True,
                never_pretend=True
            ).stdout.strip()
            self._branches = [x.strip('* \t\n') for x in out.splitlines()]

        return self._branches

    @property
    def parents(self) -> List['CommitDetails']:
        """ Parents of the this commit. """
        if self._parents is None:
            self._parents = [CommitDetails.get(x) for x in self.parents_sha1]

        return self._parents

    # TODO: remove this property, only used by GAE plugin, which is dead anyway.
    @property
    def number(self) -> int:
        """ Return this commits number.

        This is the same as the total number of commits in history up until
        this commit.

        This value can be useful in some CI scenarios as it allows to track
        progress on any given branch (although there can be two commits with the
        same number existing on different branches).

        Returns:
            int: The commit number/index.
        """
        cmd = 'git log --oneline {}'.format(self.sha1)
        out = shell.run(cmd, capture=True, never_pretend=True).stdout.strip()
        return len(out.splitlines())

    @classmethod
    def get(cls, sha1: str = '') -> 'CommitDetails':
        """ Return details about a given commit.

        Args:
            sha1 (str):
                The sha1 of the commit to query. If not given, it will return
                the details for the latest commit.

        Returns:
            CommitDetails: Commit details. You can use the instance of the
            class to query git tree further.
        """
        with conf.within_proj_dir():
            cmd = 'git show -s --format="%H||%an||%ae||%s||%b||%P" {}'.format(
                sha1
            )
            result = shell.run(cmd, capture=True, never_pretend=True).stdout

        parts = result.split('||')
        if len(parts) != 6:
            raise ValueError('Invalid git show result:\n  {}'.format(result))

        sha1, name, email, title, desc, parents = result.split('||')

        return CommitDetails(
            sha1=sha1,
            author=Author(name, email),
            title=title,
            desc=desc,
            parents_sha1=parents.split(),
        )
