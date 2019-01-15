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
""" Commands package.

All commands (and only commands) should be defined inside this package. This
should be as thin layer as possible. Ideally just processing CLI params and
displaying results.
"""
from __future__ import absolute_import

# stdlib imports
from types import FunctionType
from typing import Any

# 3rd party imports
import click

# local imports
import peltak


@click.group()
@click.version_option(version=peltak.__version__, message='%(version)s')
def root_cli():
    # type: () -> None
    """

    To get help for a specific command:

       \033[1m peltak <command> --help\033[0m

    Examples:

       \033[1m peltak lint --help\033[0m

       \033[1m peltak version bump --help\033[0m

       \033[1m peltak release upload --help\033[0m

    """
    pass


def pretend_option(fn):
    # type: (FunctionType) -> FunctionType
    """ Decorator to add a --pretend option to any click command.

    The value won't be passed down to the command, but rather handled in the
    callback. The value will be accessible through `peltak.core.context` under
    'pretend' if the command needs it. To get the current value you can do:

        >>> from peltak.commands import click, root_cli
        >>> from peltak.core import context
        >>>
        >>> @root_cli.command('my-command')
        >>> @pretend_option
        >>> def my_command():
        ...     pretend = context.get('pretend', False)

    This value will be accessible from anywhere in the code.
    """

    def set_pretend(ctx, param, value):     # pylint: disable=missing-docstring
        # type: (click.Context, str, Any) -> None
        from peltak.core import context
        from peltak.core import shell

        context.set('pretend', value or False)
        if value:
            shell.cprint('<90>{}', _pretend_msg())

    return click.option(
        '--pretend',
        is_flag=True,
        help=("Do not actually do anything, just print shell commands that"
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
        # We do empty format() here so that it forces unicode errors here
        # and not when it's used/printed.
        return '{}'.format(util.remove_indent(msg))
    except:
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

    def set_verbose(ctx, param, value):     # pylint: disable=missing-docstring
        # type: (click.Context, str, Any) -> None
        from peltak.core import context
        context.set('verbose', value or 0)

    return click.option(
        '-v', '--verbose',
        is_flag=True,
        expose_value=False,
        callback=set_verbose,
        help="Be verbose. Can specify multiple times for more verbosity.",
    )(fn)
