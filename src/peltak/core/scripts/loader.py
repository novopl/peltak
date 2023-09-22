import os
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, Iterator, List, cast

import click

from peltak.cli import peltak_cli
from peltak.core import conf, exc, log, util

from . import types


class NoScript(exc.PeltakError):
    msg = "No Script"


class CommandAlreadyExists(exc.PeltakError):
    msg = "Command Already Exists"


BUILTIN_FUNCTIONS = {
    'cprint': textwrap.dedent('''
        echo $(echo "$@<0>" | sed -E 's/<([0-9][0-9]?)>/\\x1b[\\1m/g')
    '''),
    'header': textwrap.dedent('''
        local title="$@"
        local title_len=$(echo $title | wc -m)
        local bar_len=$(( 78 - title_len ))
        local header_bar=$(head -c $bar_len < /dev/zero | tr '\\0' '=')

        echo $(echo "<32>= <35>$title <32>$header_bar<0>" \\
            | sed -E 's/<([0-9][0-9]?)>/\\x1b[\\1m/g')
    '''),
}


def register_scripts_from(scripts_dir: Path) -> None:
    """ Parse script files and build the ClI for it. """
    if not (scripts_dir.exists() and scripts_dir.is_dir()):
        # Silently return if the scripts directory does not exist. They are not
        # required and the completion should not brake so we can't raise
        # any exceptions or print anything to stdout/stderr.
        return

    for script_path in _iter_script_files(scripts_dir):
        log.dbg(f"Loading script {script_path}")

        script = _parse_script(script_path)
        rel_path = script_path.relative_to(scripts_dir)
        script_cli_path = str(rel_path).split(os.sep)[:-1]
        _register_script(script, script_cli_path)


def _iter_script_files(scripts_dir: Path) -> Iterator[Path]:
    results: List[Path] = []

    for dir_item in scripts_dir.iterdir():
        log.dbg(f"Looking for a script in {dir_item}")
        if dir_item.is_dir():
            yield from _iter_script_files(dir_item)
        elif dir_item.name.endswith('.sh'):
            yield dir_item
        elif dir_item.name.endswith('.py'):
            conf.py_import(dir_item.stem)

    return results


def _parse_script(script_path: Path) -> types.Script:
    """ Parse a script file.

    The file starts wit the file header.
    """
    script_name = script_path.name.split('.')[0]
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

        # Parse to get the header and the rest (the actual script).
        for line in lines:
            # Only the top lines are considered header, once it ends we won't
            # search for it anymore.
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

    # Check if we have the script header.
    header_yaml = '\n'.join(header_lines)
    if not header_yaml:
        raise NoScript(f"peltak header is missing from file: {script_path}")

    # Load the header yaml and make sure it's a peltak script configuration.
    header: Dict[str, Any] = cast(Dict[str, Any], util.yaml_load(header_yaml))
    if len(header) == 1 and 'peltak' in header:
        script_options = header['peltak']
    else:
        script_options = header

    script_src = _inject_builtins(
        script_conf=script_options,
        script_src='\n'.join(source_lines).strip()
    )

    return types.Script.from_config(
        name=script_name,
        script_conf={
            **script_options,
            'command': script_src,
        },
    )


def _inject_builtins(script_conf: Dict[str, Any], script_src: str) -> str:
    """ Inject all built-ins the script specifies it's using. """
    result = ''

    for fn_name in script_conf.get('use', []):
        impl = textwrap.indent(BUILTIN_FUNCTIONS.get(fn_name, ''), prefix='    ')
        if not impl:
            continue
        result += f'function {fn_name}() {{{impl}}}' + '\n'

    return f"### BUILTINS ###\n{result}### END BUILTINS ###\n{script_src}"


def _register_script(script: types.Script, cli_path: List[str]):
    parent_cli = peltak_cli

    for part in cli_path:
        parent_cli = _get_click_subgroup(parent_cli, part)

    script.register(parent_cli)


def _get_click_subgroup(cli_group: click.Group, name: str) -> click.Group:
    sub_cmd = next(
        (c for cmd_name, c in cli_group.commands.items() if cmd_name == name),
        None
    )

    if not sub_cmd:
        # Create new group as it doesn't exist yet:
        return cli_group.group(name)(lambda: None)
    elif isinstance(sub_cmd, click.Group):
        return sub_cmd
    else:
        # The given script name is already reserved by peltak or one of the loaded
        # plugins.
        raise CommandAlreadyExists(name)
