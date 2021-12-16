# Copyright 2021 Mateusz Klos
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
from datetime import datetime
from typing import List, Optional


@dataclasses.dataclass
class LineRange:
    start: int
    end: int

    def __init__(self, start: int, end: Optional[int] = None):
        self.start = start
        self.end = start if end is None else end

    def __str__(self) -> str:
        if self.start == self.end:
            return str(self.start)
        else:
            return f"{self.start}-{self.end}"


@dataclasses.dataclass
class Todo:
    file: str
    lines: LineRange
    body: List[str]
    sha1: str
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    timestamp: Optional[int] = None

    @property
    def pretty_timestamp(self) -> str:
        if self.timestamp:
            return str(datetime.fromtimestamp(self.timestamp))
        else:
            return '(not committed)'

    @property
    def author(self) -> str:
        author_name = self.author_name or 'Not Committed Yet'
        author_email = self.author_email or 'not.committed.yet'
        return f"{author_name} <{author_email}>"

    @property
    def color_text(self) -> str:
        result = f"<1>{self.body[0]}<0>"
        if len(self.body) > 1:
            result += '\n' + '\n'.join(self.body[1:])

        return result

    @property
    def text(self) -> str:
        return '\n'.join(self.body)
