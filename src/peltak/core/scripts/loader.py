import os
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, NamedTuple, Tuple, cast

from peltak.cli import peltak_cli
from peltak.core import conf, exc, util

from . import types


class ScriptId(NamedTuple):
    name: str
    path: str


class NoScript(exc.PeltakError):
    msg = "No Script"


CliGroups = Dict[str, Any]
ScriptsMap = Dict[ScriptId, types.Script]


def register_scripts_from(scripts_dir: Path) -> None:
    """ Parse script files and build the ClI for it. """
    if scripts_dir.exists() and scripts_dir.is_dir():
        # Silently return if the scripts directory does not exist. They are not
        # required and the completion should not brake so we can't raise
        # any exceptions or print anything to stdout/stderr.
        script_files = list(_iter_script_files(scripts_dir))
        scripts = _process_script_files(scripts_dir, script_files)
        cli_groups = generate_cli_groups(scripts)

        for script_id, script in scripts.items():
            cli_group = cli_groups[script_id.path]
            script.register(cli_group)


def generate_cli_groups(scripts: ScriptsMap) -> Dict[str, Any]:
    results: Dict[str, Any] = {'': peltak_cli}
    unique_paths = sorted(frozenset(x.path for x in scripts.keys() if x.path))

    for path in unique_paths:
        results[path] = _generate_cli_group(results, path)

    return results


def _iter_script_files(scripts_dir: Path) -> Iterator[Path]:
    results: List[Path] = []

    for dir_item in scripts_dir.iterdir():
        if dir_item.is_dir():
            yield from _iter_script_files(dir_item)
        # else:
        #     yield dir_item
        elif dir_item.name.endswith('.sh'):
            # We only support shell scripts this way. The user can also keep python
            # scripts in his scripts dir and those should import `peltak_cli` and
            # be registered via ``pelconf.yaml``
            # TODO: Autoload python scripts found inside `scripts_dir`.
            yield dir_item
        elif dir_item.name.endswith('.py'):
            # Auto load python scripts in scripts_dir
            conf.py_import(dir_item.stem)

    return results


def _process_script_files(scripts_dir: Path, script_files: List[Path]) -> ScriptsMap:
    results: ScriptsMap = {}

    for script_file in sorted(script_files):
        rel_path = script_file.relative_to(scripts_dir)
        script_id = _gen_script_id(rel_path)
        try:
            results[script_id] = _parse_script(script_id, script_file)
        except NoScript:
            pass

    return results


def _parse_script(script_id: ScriptId, script_path: Path) -> types.Script:
    """ Parse a script file.

    The file starts wit the file header.
    """
    re_header = re.compile(r'^# (?P<content>.*)')
    header_lines: List[str] = []
    source_lines: List[str] = []
    header_ended = False

    with script_path.open() as fp:
        lines = fp.readlines()
        if not lines:
            raise ValueError(f"Empty file {script_path}")

        if lines[0].startswith('#!'):
            lines = lines[1:]

        for line in lines:
            # Only the top lines are considered header, once it ends we won't
            # search for it anymore
            if not header_ended:
                m = re_header.match(line)
                if m:
                    content = m.group('content')
                    # An empty comment line also ends the header
                    if content.strip():
                        header_lines.append(content)
                    else:
                        header_ended = True
                    continue
                else:
                    # First line that is not a comment means it's not a header anymore
                    header_ended = True

            source_lines.append(line.rstrip())

    header_yaml = '\n'.join(header_lines)

    if not header_yaml:
        raise NoScript(f"peltak header is missing from file: {script_path}")

    header: Dict[str, Any] = cast(Dict[str, Any], util.yaml_load(header_yaml))
    if not (len(header) == 1 and 'peltak' in header):
        raise NoScript("Script header can only have a single root object 'peltak'")

    return types.Script.from_config(
        name=script_id.name,
        script_conf={
            **header['peltak'],
            'command': '\n'.join(source_lines).strip(),
        },
    )


def _gen_script_id(rel_path: Path) -> ScriptId:
    path = ' '.join(str(rel_path).split(os.sep)[:-1])
    name = rel_path.name.split('.')[0]
    return ScriptId(name, path)


def _generate_cli_group(groups: Dict[str, Any], group_path: str):
    name, parent = _parse_group_path(group_path)
    parent_cli = peltak_cli

    if parent:
        if parent in groups:
            parent_cli = groups[parent]
        else:
            parent_cli = _generate_cli_group(groups, parent)
            groups[parent] = parent_cli

    return parent_cli.group(name)(lambda: None)


def _parse_group_path(group_path: str) -> Tuple[str, str]:
    parts = group_path.rsplit(maxsplit=1)
    name = parts[-1]
    parent = parts[0] if len(parts) == 2 else ''
    return name, parent
