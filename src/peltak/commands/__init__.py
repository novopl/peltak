# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import click

import peltak


@click.group()
@click.version_option(version=peltak.__version__, message='%(version)s')
def cli():
    """

    To get help for a specific command:

        \033[1mpeltak <command> --help\033[0m

    Examples:

        \033[1mpeltak lint --help\033[0m

        \033[1mpeltak version bump --help\033[0m

        \033[1mpeltak release upload --help\033[0m

    """
    pass
