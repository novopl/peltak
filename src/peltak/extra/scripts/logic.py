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
from typing import Any, Dict, List

# local imports
from six import string_types
from peltak.core import conf
from peltak.core import log
from peltak.commands import click
from .types import Script


_j2_env = None


def init_jinja2():
    # type: () -> None
    """ Initialize jinja2 env. """
    global _j2_env

    import jinja2
    from peltak.core import shell
    from peltak.core import fs

    _j2_env = jinja2.Environment(
        variable_start_string='{{',
        variable_end_string='}}',
    )

    ###########
    # Filters #
    ###########
    def section(title):
        """ Returns '= {title} =========================' """
        remaining = 80 - len(title) - 3
        return shell.fmt('<32>= <35>{title} <32>{bar}<0>',
                         title=title,
                         bar='=' * remaining)

    def count_flag(count, flag):
        """ Returns the given flag letter as a count flag.

        This will
        """
        return '-' + flag * count if count else ''

    _j2_env.filters['wrap_paths'] = fs.wrap_paths
    _j2_env.filters['section'] = section
    _j2_env.filters['count_flag'] = count_flag


def _build_template_context(script, ctx, options, conf, click_ctx, gitignore):
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
        'conf': conf.g_config,
        'ctx': ctx.values,
        'click': click_ctx,
        'proj_path': conf.proj_path,
    }

    if script.accept_files:
        exclude = list(options['exclude'])
        exclude += gitignore

        template_ctx['files'] = collect_files(
            options['paths'],
            options['exclude'],
            options['skip_untracked'],
            options['commit_only']
        )

    return template_ctx


def collect_files(paths, exclude, skip_untracked, commit_only):
    # type: (List[str], List[str], bool, bool) -> List[str]
    """ Collect files based on the command line options.

    This will work with the command line options defined by 'files_options'.
    """
    import itertools
    from peltak.core import fs
    from peltak.core import git

    paths = [conf.proj_path(p) for p in paths]
    exclude = list(exclude)

    # prepare
    if commit_only:
        include = ['*' + f for f in git.staged()]
        exclude += git.ignore()
    else:
        include = ['*']

    if skip_untracked:
        exclude += git.untracked()

    if isinstance(paths, string_types):
        raise ValueError("paths must be an array of strings")

    return list(itertools.chain.from_iterable(
        fs.filtered_walk(p, include, exclude) for p in paths
    ))


def run_script(script, click_ctx, options):
    # type: (Script, click.Context, Dict[str, Any]) -> None
    """ Run the script with the given (command line) options. """
    import yaml
    from peltak.core import git
    from peltak.core import shell
    from peltak.core.context import GlobalContext

    ctx = GlobalContext()
    template_ctx = _build_template_context(
        script,
        ctx=ctx,
        options=options,
        conf=conf,
        click_ctx=click_ctx,
        gitignore=git.ignore(),
    )

    if ctx.get('verbose') > 1:
        log.info('Compiling script <35>{name}\n{script}'.format(
            name=script.name,
            script=shell.highlight(script.command, 'jinja')
        ))
        log.info('with context:\n{}\n'.format(
            shell.highlight(yaml.dump(template_ctx), 'yaml')
        ))

    if _j2_env is None:
        init_jinja2()

    cmd = _j2_env.from_string(script.command).render(template_ctx)

    with conf.within_proj_dir():
        if ctx.get('verbose'):
            log.info(
                "Running script: <35>{name}\n<90>{bar}<0>\n{script}\n<90>{bar}",
                name=script.name,
                bar='-' * 80,
                script=shell.highlight(cmd, 'bash'),
            )
        return shell.run(cmd)


# Used only in type hint comments.
del Dict, Any, List, click, Script
