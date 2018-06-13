# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import click_completion

# local imports
from peltak.common import conf
from peltak.commands_old import cli
__all__ = [
    'cli'
]


conf.load()
click_completion.init()
