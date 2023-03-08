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
"""
.. module:: peltak.core.log
    :synopsis: Helpers for nice shell output formatting.
"""
import os
from typing import Any

from . import context, exc, shell


def info(msg: str, *args: Any, **kw: Any) -> None:
    """ Print sys message to stdout.

    System messages should inform about the flow of the script. This should
    be a major milestones during the build.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <32>{}<0>'.format(msg))


def err(msg: str, *args: Any, **kw: Any) -> None:
    """ Per step status messages

    Use this locally in a command definition to highlight more important
    information.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <31>{}<0>'.format(msg))


def detail(msg: str, *args: Any, **kw: Any) -> None:
    """ Detail level logs, only visible with -v flag. """
    if get_verbosity() < 1:
        return

    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <0>{}<0>'.format(msg))


def dbg(msg: str, *args: Any, **kw: Any) -> None:
    """ Debug level logs, only visible with -vvv flag. """
    if get_verbosity() < 3:
        return

    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <90>{}<0>'.format(msg))


def get_verbosity() -> int:
    """ Get the current verbosity level.

    This can be set either using the -v/--verbose option or via env variable
    PELTAK_VERBOSE. The CLI will override the env variable if set. The reason for that
    is that some of the internals of peltak run before the options are parsed and thus
    the value given via CLI is not available yet. For this type of bug investigation,
    you can use the env variable.

    The code should use this function instead of just doing ``context.get('verbose')``.
    """
    if context.has('verbose'):
        return context.get('verbose')
    else:
        str_value = os.environ.get('PELTAK_VERBOSE', '0')
        if not str_value.isdigit():
            raise exc.PeltakError('PELTAK_VERBOSE env variable is not a digit')

        return int(str_value)
