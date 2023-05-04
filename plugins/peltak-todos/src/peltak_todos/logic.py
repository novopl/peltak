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
import itertools
import sys
import textwrap
from pathlib import Path
from typing import Collection, FrozenSet, List

from peltak.core import context, fs, git, log, shell

from . import parser
from .types import Todo


def check_todos(
    input_paths: Collection[str],
    authors: List[str],
    verify_complete: bool,
) -> None:
    input_files = _collect_input_files(input_paths)
    todos = parser.extract_from_files(list(input_files))
    filtered_todos = [
        t for t in todos
        if not authors or any(
            a.lower() in t.author.lower() for a in authors
        )
    ]
    _render_todos(filtered_todos)

    if verify_complete and len(filtered_todos) > 0:
        sys.exit(127)


def _collect_input_files(input_paths: Collection[str], ) -> FrozenSet[Path]:
    repo_path = Path(
        shell.run("git rev-parse --show-toplevel", capture=True).stdout.strip()
    )
    input_files: FrozenSet[Path] = frozenset()

    for input_path in input_paths:
        if input_path == ':commit':
            input_files |= frozenset([
                repo_path / fpath
                for fpath in (git.staged() + git.unstaged())
            ])
        elif input_path == ':diff':
            input_files |= frozenset(
                repo_path / fpath
                for fpath in (
                    parser.get_changed_files(base_branch='master')
                )
                if (repo_path / fpath).exists()
            )
        elif input_path == ':untracked':
            input_files |= frozenset([
                (repo_path / fpath) for fpath in git.untracked()
            ])
        else:
            path = Path(input_path)
            if path.is_dir():
                input_files |= frozenset(
                    Path(f) for f in fs.filtered_walk(str(path))
                    if not Path(f).is_dir()
                )
            else:
                input_files |= frozenset([path])

    return input_files


def _render_todos(todos: List[Todo]) -> None:
    by_file = sorted(
        # Convert the iterators to lists so we can go over them multiple times
        [(x[0], list(x[1])) for x in itertools.groupby(todos, key=lambda x: x.file)],
        key=lambda x: x[0],
    )

    print('\n')
    for file_path, file_todos in by_file:
        sorted_todos = sorted(file_todos, key=lambda x: x.lines.start)

        shell.cprint(f"<92>{file_path}\n")
        for todo in sorted_todos:
            if context.get('verbose') >= 1:
                shell.cprint(
                    f"<36>{todo.pretty_timestamp}  <33>{todo.author}<0>\n"
                    f"<95>{todo.file}:{todo.lines}  <90>{todo.sha1}<0>\n\n"
                    f"{textwrap.indent(todo.color_text, '  ')}\n\n"
                )
            else:
                shell.cprint(
                    f"    <95>:{todo.lines}  <36>{todo.pretty_timestamp}  "
                    f"<33>{todo.author_email}  <90>{todo.sha1}<0><0>\n\n"
                    f"{textwrap.indent(todo.color_text, '        ')}\n"
                )
        print()

    log.info(f"Found <33>{len(todos)}<32> TODOs")
