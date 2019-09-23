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

# 3rd party imports
import attr

# local imports
from six import string_types
from peltak.core import conf
from peltak.core import log
from peltak.commands import click, pretend_option, verbose_option


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


@attr.s
class ScriptOption(object):
    """ Describes the scripts command line option. """
    name = attr.ib(type=List[str])
    default = attr.ib(type=Any, default=None)
    about = attr.ib(type=str, default='')
    is_flag = attr.ib(type=bool, default=False)

    @classmethod
    def from_config(cls, option_conf):
        # type: (Dict[str, Any]) -> ScriptOption
        """ Load script option from configuration in pelconf.yaml """
        fields = attr.fields(cls)
        name = option_conf.get('name')

        if not name:
            raise ValueError("You must define the name of the option")

        if isinstance(name, string_types):
            # Support passing name: ['--opt'] or name: '--opt'
            name = [name]

        return cls(
            name=name,
            default=option_conf.get('default', fields.default.default),
            about=option_conf.get('about', fields.about.default),
            is_flag=option_conf.get('is_flag', fields.is_flag.default)
        )


@attr.s
class Script(object):
    """ Represents a single script defined in pelconf.yaml.

    The important thing is to do a little as possible during creation and only
    do heavy stuff inside the `Script.run()` method. This is because the
    scripts are parsed in a *post-conf-load* hook and that code impacts the
    speed of shell auto completion for peltak command.
    """
    name = attr.ib(type=str)
    command = attr.ib(type=str)
    about = attr.ib(type=str, default='')
    accept_files = attr.ib(type=str, default=False)
    options = attr.ib(type=List[ScriptOption], default=[])

    @classmethod
    def from_config(cls, name, script_conf):
        # type: (str, Dict[str, Any]) -> Script
        """ Load script from pelfconf.yaml """
        fields = attr.fields(cls)

        if 'command' not in script_conf:
            raise ValueError("Missing 'command' for '{}' script".format(name))

        return cls(
            name=name,
            command=script_conf['command'],
            about=script_conf.get('about', fields.about.default),
            accept_files=script_conf.get('accept_files', fields.about.default),
            options=[
                ScriptOption.from_config(opt_conf)
                for opt_conf in script_conf.get('options', fields.options.default)
            ]
        )

    def run(self, click_ctx, options):
        # type: (click.Context, Dict[str, Any]) -> None
        """ Run the script with the given (command line) options. """
        import yaml
        from peltak.core import git
        from peltak.core import shell
        from peltak.core.context import GlobalContext

        ctx = GlobalContext()
        template_ctx = _build_template_context(
            self,
            ctx=ctx,
            options=options,
            conf=conf,
            click_ctx=click_ctx,
            gitignore=git.ignore(),
        )

        if ctx.get('verbose') > 1:
            log.info('Compiling script <35>{name}\n{script}'.format(
                name=self.name,
                script=shell.highlight(self.command, 'jinja')
            ))
            log.info('with context:\n{}\n'.format(
                shell.highlight(yaml.dump(template_ctx), 'yaml')
            ))

        if _j2_env is None:
            init_jinja2()

        cmd = _j2_env.from_string(self.command).render(template_ctx)

        with conf.within_proj_dir():
            if ctx.get('verbose'):
                log.info(
                    "Running script: <35>{name}\n<90>{bar}<0>\n{script}\n<90>{bar}",
                    name=self.name,
                    bar='-' * 80,
                    script=shell.highlight(cmd, 'bash'),
                )
            return shell.run(cmd)

    def register(self, cli_group):
        # type: (click.Group) -> None
        """ Register the script with click. """
        @pretend_option
        @verbose_option
        @click.pass_context
        def script_command(ctx, **options):  # pylint: disable=missing-docstring
            self.run(click_ctx=ctx, options=options)

        script_command.__doc__ = self.about

        if self.accept_files:
            script_command = files_options(script_command)

        cli_group.command(self.name)(script_command)


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


def files_options(fn):
    """ Decorate command with options that allow passing and filtering files. """
    fn = click.option(
        '-e', '--exclude',
        multiple=True,
        metavar='PATTERN',
        help=(
            "Specify patterns to exclude from linting. For multiple patterns, "
            "use the --exclude option multiple times"
        )
    )(fn)
    fn = click.option(
        '-i', '--include',
        multiple=True,
        metavar='PATTERN',
        help=(
            "Specify patterns to include from linting. For multiple patterns, "
            "use the --include option multiple times. This is a white list "
            "filter."
        )
    )(fn)
    fn = click.option(
        '--skip-untracked',
        is_flag=True,
        help="Also include files not tracked by git."
    )(fn)
    fn = click.option(
        '--commit', 'commit_only',
        is_flag=True,
        help=(
            "Only lint files staged for commit. Useful if you want to clean up "
            "a large code base one commit at a time."
        )
    )(fn)
    fn = click.argument(
        'paths',
        type=click.Path(exists=True),
        nargs=-1,
    )(fn)
    return fn


# Used only in type hint comments.
del Dict
