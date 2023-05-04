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
""" CLI Commands

The commands should be split into separate py modules, one with the command
click declaration and a separate implementation module. This is to reduce the number
of imports required when loading the CLI for autocompletion. It doesn't change much
for one command module, but makes a big difference when applied to all commands
used by the given peltak configuration. This way the commands module contain only code
used by click to generate the completion and everything else is imported when a given
command is executed.
"""
from typing import Any, Callable, Union

import click

import peltak


AnyFn = Callable[..., Any]


def pretend_option(fn: AnyFn) -> AnyFn:
    """ Decorator to add a --pretend option to any click command.

    The value won't be passed down to the command, but rather handled in the
    callback. The value will be accessible through `peltak.core.context` under
    'pretend' if the command needs it. To get the current value you can do:

        >>> from peltak.cli import click, peltak_cli
        >>> from peltak.core import context
        >>>
        >>> @peltak_cli.command('my-command')
        ... @pretend_option
        ... def my_command():
        ...     pretend = context.get('pretend', False)

    This value will be accessible from anywhere in the code.
    """

    def set_pretend(     # pylint: disable=missing-docstring
        ctx: click.Context,
        param: Union[click.Option, click.Parameter],
        value: Any
    ) -> Any:
        from peltak.core import context, shell

        context.set('pretend', value or False)
        if value:
            shell.cprint('<90>{}', _pretend_msg())

    return click.option(
        '--pretend',
        is_flag=True,
        help=("Do not actually do anything, just print shell commands that "
              "would be executed."),
        expose_value=False,
        callback=set_pretend
    )(fn)


def _pretend_msg():
    from peltak.core import util
    msg = '''
        ┌─────────────────────────────────────────────────────────────────┐
        │                     Running in pretend mode.                    │
        ├─────────────────────────────────────────────────────────────────┤
        │ All commands that you will see printed in gray are not actually │
        │ executed but printed out instead.                               │
        │                                                                 │
        │ Those would be executed if --pretend option was not specified.  │
        │                                                                 │
        │ You can still add verbosity to some commands using the          │
        │ -v/--verbose option.                                            │
        └─────────────────────────────────────────────────────────────────┘
    '''

    if hasattr(msg, 'decode'):  # py2
        msg = msg.decode('utf-8')

    try:
        # We do empty format() so that it forces unicode errors to happen here
        # and not when it's used/printed.
        return '{}'.format(util.remove_indent(msg))
    except Exception:
        # Pretty printing the frame is not supported - fallback to raw ASCII.
        return util.remove_indent('''
        +-----------------------------------------------------------------+
        |                     Running in pretend mode.                    |
        +-----------------------------------------------------------------+
        | All commands that you will see printed in gray are not actually |
        | executed but printed out instead.                               |
        |                                                                 |
        | Those would be executed if --pretend option was not specified.  |
        |                                                                 |
        | You can still add verbosity to some commands using the          |
        | -v/--verbose option.                                            |
        +-----------------------------------------------------------------+
    ''')


def verbose_option(fn):
    """ Decorator to add a --verbose option to any click command.

    The value won't be passed down to the command, but rather handled in the
    callback. The value will be accessible through `peltak.core.context` under
    'verbose' if the command needs it. To get the current value you can do:

        >>> from peltak.core import context
        >>>
        >>> pretend = context.get('verbose', False)

    This value will be accessible from anywhere in the code.
    """

    def set_verbose(    # pylint: disable=missing-docstring
        ctx: click.Context,
        param: Union[click.Option, click.Parameter],
        value: Any
    ) -> Any:
        from peltak.core import context
        context.set('verbose', value or 0)

    return click.option(
        '-v', '--verbose',
        expose_value=False,
        count=True,
        callback=set_verbose,
        help="Be verbose. Can specify multiple times for more verbosity.",
    )(fn)


@click.group()
@click.version_option(version=peltak.__version__, message='%(version)s')
@verbose_option
@click.pass_context
def peltak_cli(ctx: click.Context) -> None:
    """

    To get help for a specific command:

       \033[1m peltak <command> --help\033[0m

    Examples:

       \033[1m peltak lint --help\033[0m

       \033[1m peltak version bump --help\033[0m

       \033[1m peltak release upload --help\033[0m

    """
    pass
