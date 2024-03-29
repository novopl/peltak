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
""" Types and classes used by `peltak.extra.changelog`. """
import dataclasses
from typing import Any, Dict, List


ChangelogItems = Dict[str, List[Any]]


@dataclasses.dataclass
class ChangelogTag:
    """ Changelog tag config.

    This is used to map the tags used in commit message details to the actual
    headers used in the generated changelog.

    Attributes:
        header (str):   The header used in the generated changelog.
        tag (str):      The tag used in commit message details.

    """
    header: str
    tag: str
