# Copyright 2017-2020 Mateusz Klos
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
""" scripts logic. """
import dataclasses
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import yaml

from peltak.core import conf, fs, log, shell, templates
from peltak.core.context import RunContext

from .types import CliOptions, Script


def run_script(script: Script, options: CliOptions) -> None:
    """ Run the script with the given (command line) options. """
    template_ctx = build_template_context(script, options)
    verbose = log.get_verbosity()
    pretend = RunContext().get('pretend')

    if verbose >= 3:
        log.dbg('Compiling script <35>{name}\n{script}'.format(
            name=script.name,
            script=shell.highlight(script.command, 'jinja')
        ))
        yaml_str = yaml.dump(template_ctx, default_flow_style=False)
        log.dbg('with context:\n{}\n'.format(shell.highlight(yaml_str, 'yaml')))

    # Command is either specified directly in pelconf.yaml or lives in a
    # separate file.
    command = script.command
    if script.command_file:
        with open(conf.proj_path(script.command_file)) as fp:
            command = fp.read()

    if not command:
        raise ValueError("Scripts must have 'command' or 'command_file' specified.")

    cmd = templates.Engine().render(command, template_ctx)
    retcode = exec_script_command(cmd, pretend)

    log.detail(f"Script exited with code: <33>{retcode}")

    if retcode not in script.success_exit_codes:
        sys.exit(retcode)


def exec_script_command(cmd: str, pretend: bool) -> int:
    """ This will execute the already compiled script command.

    This function serves the purpose of encapsulating the low level code of
    spawning a subprocess from the rest of the logic.
    """
    if not pretend:
        with conf.within_proj_dir():
            # God knows why, if we run the command using `shell.run()` and it
            # exists with non-zero code it will also kill the parent peltak
            # process. The Popen arguments are the same, to my knowledge
            # everything is the same but the way it behaves is completely
            # different. If we just use Popen directly, everything works as
            # expected  ¯\_(ツ)_/¯
            # TODO: This possibly happens because of exit_on_error in shell.run()
            p = subprocess.Popen(
                cmd,
                shell=True,
                # Replacement shell to use
                # TODO: This works on POSIX systems, might cause problems on windows.
                executable=_default_shell(),
            )
            try:
                p.communicate()
                return p.returncode
            except KeyboardInterrupt:
                p.kill()
                return -1
    else:
        log.info(
            "<90>{bar}<0>\n{script}\n<90>{bar}",
            bar='=' * 80,
            script=shell.highlight(cmd, 'bash'),
        )
        return 0


def build_template_context(script, options):
    """ Build command template context.

    This will collect all the values like current configuration, command line
    options, runtime context etc. and pass it to the script template.
    """
    template_ctx = {
        'opts': dict(
            verbose=log.get_verbosity(),
            pretend=RunContext().get('pretend'),
            **options
        ),
        'script': dataclasses.asdict(script),
        'conf': conf.as_dict(),
        'ctx': RunContext().values,
        'proj_path': conf.proj_path,
    }

    if script.files:
        template_ctx['files'] = fs.collect_files(script.files)

    return template_ctx


def _default_shell() -> Optional[str]:
    default_shell = os.environ.get('SHELL', None)

    if default_shell in (None, '/bin/sh') and Path('/bin/bash').exists():
        default_shell = '/bin/bash'

    return default_shell
