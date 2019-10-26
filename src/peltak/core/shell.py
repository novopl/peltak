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
"""
.. module:: peltak.core.shell
    :synopsis: Shell related helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import re
import subprocess
import sys
from typing import Any, Dict

# 3rd party imports
import attr

# local imports
from . import context


EnvDict = Dict[str, str]


@attr.s
class ExecResult(object):
    """ Encapsulates a `shell.run` result.

    Attributes:
        command (str):
            The command that was executed.
        return_code (int):
            The command exit code.
        stdout (str):
            The command standard output content after the execution.
        stderr (str):
            The command standard error content after the execution.
        succeeded (bool):
            **True** if command was successful (return_code was 0 or the one
            that was expected).
        failed (bool):
            **True** if command failed.

    """
    command = attr.ib(type=str)
    return_code = attr.ib(type=int)
    stdout = attr.ib(type=str)
    stderr = attr.ib(type=str)
    succeeded = attr.ib(type=bool)
    failed = attr.ib(type=bool)


is_tty = sys.stdout.isatty()


def decolorize(text):
    # type: (str) -> str
    """ Remove all opcodes from the text.

    Args:
        text (str):
            Source text that includes color opcodes as used in `shell.fmt`
            function.

    Returns:
        str: The same text but with all opcodes removed.
    """
    return re.sub(r'<(\d{1,2})>', '', text)


def fmt(msg, *args, **kw):
    # type: (str, *Any, **Any) -> str
    """ Generate shell color opcodes from a pretty coloring syntax. """
    global is_tty

    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    opcode_subst = '\x1b[\\1m' if is_tty else ''
    return re.sub(r'<(\d{1,2})>', opcode_subst, msg)


def cprint(msg, *args, **kw):
    # type: (str, *Any, **Any) -> None
    """ Print colored message to stdout. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    print(fmt('{}<0>'.format(msg)))


def run(cmd,
        capture=False,
        shell=True,
        env=None,
        exit_on_error=None,
        never_pretend=False):
    # type: (str, bool, bool, EnvDict, bool, bool) -> ExecResult
    """ Run a shell command.

    Args:
        cmd (str):
            The shell command to execute.
        shell (bool):
            Same as in `subprocess.Popen`.
        capture (bool):
            If set to True, it will capture the standard input/error instead of
            just piping it to the caller stdout/stderr.
        env (dict[str, str]):
            The subprocess environment variables.
        exit_on_error (bool):
            If set to **True**, on failure it will call `sys.exit` with the
            return code for the executed command.
        never_pretend (bool):
            If set to **True** the command will always be executed, even if
            context.get('pretend') is set to True. If set to **False** or not
            given, if the ``pretend`` context value is **True**, this function
            will only print the command it would execute and then return
            a fake result.

    Returns:
        ExecResult: The execution result containing the return code and output
        (if capture was set to *True*).
    """
    if context.get('pretend', False) and not never_pretend:
        cprint('<90>{}', cmd)
        return ExecResult(
            cmd,
            0,              # retcode
            '',             # stdout
            '',             # stderr
            True,           # succeeded
            False,          # failed
        )

    if context.get('verbose', 0) > 2:
        cprint('<90>{}', cmd)

    options = {
        'bufsize': 1,       # line buffered
        'shell': shell
    }   # type: Dict[str, Any]

    if exit_on_error is None:
        exit_on_error = not capture

    if capture:
        options.update({
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        })

    if env is not None:
        options['env'] = dict(os.environ)
        options['env'].update(env)

    p = subprocess.Popen(cmd, **options)

    try:
        stdout, stderr = p.communicate()

        try:
            if stdout is not None:
                stdout = stdout.decode('utf-8')

            if stderr is not None:
                stderr = stderr.decode('utf-8')
        except AttributeError:
            # 'str' has no attribute 'decode'
            pass

        if exit_on_error and p.returncode != 0:
            sys.exit(p.returncode)

        return ExecResult(
            cmd,
            p.returncode,
            stdout,
            stderr,
            p.returncode == 0,
            p.returncode != 0
        )

    except KeyboardInterrupt:
        p.kill()
        raise


def highlight(code, fmt):
    # type: (str, str) -> str
    """ Highlight a given code snippet for printing in the terminal.

    Assumes 256 color terminal.
    """
    import pygments
    from pygments.lexers.data import YamlLexer
    from pygments.lexers.data import JsonLexer
    from pygments.lexers.python import PythonLexer
    from pygments.lexers.python import Python3Lexer
    from pygments.lexers.templates import DjangoLexer
    from pygments.lexers.shell import BashLexer
    from pygments.formatters.terminal256 import Terminal256Formatter

    # Get lexer class based on format.
    lexer_cls = {
        'yaml': YamlLexer,
        'json': JsonLexer,
        'bash': BashLexer,
        'py': Python3Lexer,
        'py3': Python3Lexer,
        'py2': PythonLexer,
        'jinja': DjangoLexer,
        'django': DjangoLexer,
    }.get(fmt)

    if not lexer_cls:
        raise ValueError("Unsupported code format: {}".format(fmt))

    return pygments.highlight(code, lexer_cls(), Terminal256Formatter())


# Used in docstrings only until we drop python2 support
del Any, Dict
