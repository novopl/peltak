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
from typing import List

from .. import conf, shell, util


@util.cached_result()
def untracked() -> List[str]:
    """ Return a list of untracked files in the project repository.

    Returns:
        list[str]: The list of files not tracked by project git repo.
    """
    with conf.within_proj_dir():
        status = shell.run(
            'git status --porcelain',
            capture=True,
            never_pretend=True
        ).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status.startswith('?? '):
                results.append(file_status[3:].strip())

        return results


@util.cached_result()
def unstaged() -> List[str]:
    """ Return a list of unstaged files in the project repository.

    Returns:
        list[str]: The list of files not tracked by project git repo.
    """
    with conf.within_proj_dir():
        status = shell.run(
            'git status --porcelain',
            capture=True,
            never_pretend=True
        ).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status.strip() and file_status[0] == ' ':
                results.append(file_status[3:].strip())

        return results


@util.cached_result()
def staged() -> List[str]:
    """ Return a list of project files staged for commit.

    Returns:
        list[str]: The list of project files staged for commit.
    """
    with conf.within_proj_dir():
        status = shell.run(
            'git status --porcelain',
            capture=True,
            never_pretend=True
        ).stdout
        results = []

        for file_status in status.split(os.linesep):
            if file_status and file_status[0] in ('A', 'M', 'D'):
                results.append(file_status[3:].strip())

        return results
