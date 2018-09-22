# -*- coding: utf-8 -*-
""" Shell related functions """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import re
import subprocess
import sys
from collections import namedtuple


ExecResult = namedtuple(
    'ExecResult',
    'command return_code stdout stderr succeeded failed'
)


is_tty = sys.stdout.isatty()


def fmt(msg, *args, **kw):
    """ Generate shell color opcodes from a pretty coloring syntax. """
    global is_tty

    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    opcode_subst = '\x1b[\\1m' if is_tty else ''
    return re.sub(r'<(\d{1,2})>', opcode_subst, msg)


def cprint(msg, *args, **kw):
    """ Print colored message to stdout. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    print(fmt('{}<0>'.format(msg)))


def run(cmd, capture=False, shell=True, env=None, exit_on_error=None):
    """ Run a shell command.

    :param str cmd:
        The shell command to execute.
    :param bool shell:
        Same as in `subprocess.Popen()`.
    :param bool capture:
        If set to True, it will capture the standard input/error instead of
        just piping it to the caller stdout/stderr.
    :param dict env:
        The subprocess environment variables.
    :param bool exit_on_error:
        If set to *True* (default), on failure it will call `sys.exit()` with
        the return code for the executed command.
    :return ExecResult:
        Return instance of ``ExecResult``. The result contains the return code
        and output (if capture was set to *True*).
    """
    options = {
        'bufsize': 1,       # line buffered
        'shell': shell
    }

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
