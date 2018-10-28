# -*- coding: utf-8 -*-
""" Commands package.

All commands (and only commands) should be defined inside this package. This
should be as thin layer as possible. Ideally just processing CLI params and
displaying results.
"""
from __future__ import absolute_import

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
