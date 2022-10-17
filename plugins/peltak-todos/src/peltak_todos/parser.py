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
import hashlib
import re
from datetime import datetime
from typing import List

from peltak.core import conf, context, shell

from .types import LineRange, Todo


def get_changed_files(base_branch: str = 'master') -> List[str]:
    result = shell.run(
        f"git diff --name-only HEAD..$(git merge-base HEAD {base_branch})",
        capture=True,
    )
    return result.stdout.splitlines()


def extract_from_files(files: List[str]) -> List[Todo]:
    parser = TodoParser(
        comment_token=conf.get('todos.comment_token', '#'),
        todo_token=conf.get('todos.todo_token', 'TODO'),
    )

    return parser.extract_todos(files)


@dataclasses.dataclass
class TodoDetails:
    author_name: str
    author_email: str
    author_time: int


class TodoParser:
    def __init__(self, comment_token: str = '#', todo_token: str = 'TODO'):
        self.comment_token = comment_token
        self.todo_token = todo_token
        self.re_name = re.compile(r'^author (?P<name>.*)$')
        self.re_mail = re.compile(r'^author-mail <(?P<mail>[^\s]+)>$')
        self.re_time = re.compile(r'^author-time (?P<time>\d+)$')
        self.re_todo = re.compile(
            f"(?P<prefix>.*?){comment_token} {todo_token}: (?P<text>.*)"
        )

    def extract_todos(self, files: List[str]) -> List[Todo]:
        todos: List[Todo] = []

        for path in files:
            file_todos = self._process_file(path)
            todos += file_todos

            if context.get('verbose') >= 1:
                if len(file_todos) > 0:
                    shell.cprint(
                        "    <33>{:2} <32>TODOs in <90>{}".format(len(file_todos), path)
                    )
                else:
                    shell.cprint("    <32>No TODOs in <90>{}".format(path))

        return todos

    def _process_file(self, path: str) -> List[Todo]:
        todos: List[Todo] = []
        line_no = 0

        # Ignore binary files
        with open(path, 'rb') as fp_bin:
            header = fp_bin.read(1024)

        if _is_binary_data(header):
            return []

        with open(path) as fp:
            line = fp.readline()
            line_no += 1

            while line:
                m = self.re_todo.match(line)
                if m:
                    start_line = line_no
                    body = [m.group('text')]

                    # Read the rest of the todo
                    continuation_re = self._continuation_regex(m.group('prefix'))
                    line = fp.readline()
                    while line:
                        line_no += 1
                        m = continuation_re.match(line)
                        if m:
                            body.append(m.group('text'))
                        else:
                            break

                        line = fp.readline()

                    # Store the todo in the result list
                    lines = LineRange(start_line, line_no - 1)
                    details = self._get_todo_details(path, lines)
                    todo = Todo(
                        file=str(path),
                        lines=lines,
                        author_name=details.author_name,
                        author_email=details.author_email,
                        body=body,
                        timestamp=details.author_time,
                        sha1=hashlib.sha1('\n'.join(body).encode('utf-8')).hexdigest(),
                    )
                    todos.append(todo)
                else:
                    line = fp.readline()
                    line_no += 1

        return todos

    def _continuation_regex(self, prefix: str) -> re.Pattern:
        return re.compile(f"{prefix}{self.comment_token} \\s+(?P<text>.*)")

    def _get_todo_details(self, file_path: str, lines: LineRange) -> TodoDetails:
        result = shell.run(
            f"git blame {file_path} -L {lines.start},{lines.end} -p",
            capture=True
        )

        author_name = 'Not Committed Yet'
        author_email = 'not.committed.yet'
        author_time = int(datetime.now().timestamp())

        for line in result.stdout.splitlines():
            m = self.re_name.match(line)
            if m:
                author_name = m.group('name')
            else:
                m = self.re_mail.match(line)
                if m:
                    author_email = m.group('mail')
                else:
                    m = self.re_time.match(line)
                    if m:
                        author_time = int(m.group('time'))

        return TodoDetails(
            author_name=author_name,
            author_email=author_email,
            author_time=author_time
        )


def _is_binary_data(data: bytes) -> bool:
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
    return bool(data.translate(None, text_chars))
