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
"""
.. module:: peltak.core.git
    :synopsis: Git helpers.
"""
from .branch import (  # noqa:  F401
    branches,
    commit_branches,
    commit_details,
    current_branch,
    guess_base_branch,
    latest_commit,
    protected_branches,
    verify_branch,
)
from .status import staged, unstaged, untracked  # noqa:  F401
from .types import Author, BranchDetails, CommitDetails  # noqa:  F401
from .util import commit_author, config, ignore, tag, tags  # noqa:  F401
