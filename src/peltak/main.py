# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import click_completion

# local imports
from peltak.core import conf
from peltak.commands import cli
__all__ = [
    'cli'
]


conf.load()
click_completion.init()
