# -*- coding: utf-8 -*-
"""
Helpers for nice shell output formatting.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from . import shell


def info(msg, *args, **kw):
    """ Print sys message to stdout.

    System messages should inform about the flow of the script. This should
    be a major milestones during the build.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <32>{}<0>'.format(msg))


def err(msg, *args, **kw):
    """ Per step status messages

    Use this locally in a command definition to highlight more important
    information.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <31>{}<0>'.format(msg))
