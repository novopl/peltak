# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
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

# stdlib imports
import itertools
import subprocess
import sys
from typing import Any, Dict, List

# 3rd party imports
import attr
import yaml

# local imports
from peltak.commands import click
from peltak.core import conf
from peltak.core import log
from peltak.core import fs
from peltak.core import shell
from peltak.core.context import GlobalContext
from . import filters
from .types import CliOptions, Script
from .templates import TemplateEngine


ctx = GlobalContext()


def run_script(script, options):
    # type: (Script, CliOptions) -> None
    """ Run the script with the given (command line) options. """
    template_ctx = _build_template_context(script, options)
    verbose = ctx.get('verbose')
    pretend = ctx.get('pretend')

    if verbose > 1:
        log.info('Compiling script <35>{name}\n{script}'.format(
            name=script.name,
            script=shell.highlight(script.command, 'jinja')
        ))
        log.info('with context:\n{}\n'.format(
            shell.highlight(yaml.dump(template_ctx), 'yaml')
        ))

    cmd = TemplateEngine().render(script.command, template_ctx)

    if not pretend:
        with conf.within_proj_dir():
            # God knows why, if we run the command using `shell.run()` and it
            # exists with non-zero code it will also kill the parent peltak
            # process. The Popen arguments are the same, to my knowledge
            # everything is the same but the way it behaves is completely
            # different. If we just use Popen directly, everything works as
            # expected  ¯\_(ツ)_/¯
            p = subprocess.Popen(cmd, shell=True)
            try:
                p.communicate()
                if verbose:
                    log.info("Script exited with code: <33>{}", p.returncode)

                if p.returncode not in script.success_exit_codes:
                    sys.exit(p.returncode)

            except KeyboardInterrupt:
                p.kill()
    else:
        log.info(
            "Would run script: <35>{name}\n<90>{bar}<0>\n{script}\n<90>{bar}",
            name=script.name,
            bar='=' * 80,
            script=shell.highlight(cmd, 'bash'),
        )


def _build_template_context(script, options):
    """ Build command template context.

    This will collect all the values like current configuration, command line
    options, runtime context etc. and pass it to the script template.
    """
    template_ctx = {
        'opts': dict(
            vebose=ctx.get('verbose'),
            pretend=ctx.get('pretend'),
            **options
        ),
        'script': attr.asdict(script),
        'conf': conf.g_config,
        'ctx': ctx.values,
        'proj_path': conf.proj_path,
        'cprint': filters.cprint,
    }

    if script.files:
        template_ctx['files'] = collect_files(script.files)

    return template_ctx


def collect_files(files):
    """ Collect script files using the given configuration. """
    paths = [conf.proj_path(p) for p in files.paths]

    return list(itertools.chain.from_iterable(
        fs.filtered_walk(path, files.whitelist(), files.blacklist())
        for path in paths
    ))


# Used only in type hint comments.
del Dict, Any, List, click, CliOptions, Script
