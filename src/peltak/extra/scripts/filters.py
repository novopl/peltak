# -*- coding: utf-8 -*-
"""
################################
Built-in script template filters
################################

All filters provided by jinja2 (list `here
<https://jinja.palletsprojects.com/en/2.10.x/templates/#list-of-builtin-filters>`_).

.. module:: peltak.extra.scripts.filters
    :synopsis: Built-in script template filters

"""
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import shell


def header(title):
    # type: (str) -> str
    """ Converts a given title into a pretty header with colors.

    **Usage:**

    .. code-block:: django

        {{ 'hello' | header }}

    will result in::

        = hello ================================================================

    The resulting string will be colored for printing in the terminal.
    """
    remaining = 80 - len(title) - 3
    return shell.fmt('<32>= <35>{title} <32>{bar}<0>',
                     title=title,
                     bar='=' * remaining)


def count_flag(count, flag):
    # type: (int, str) -> str
    """ Returns the given flag letter as a count flag.

    **Usage:**

    .. code-block:: django

        {{ 3 | count_flag('v') }}

    will result in::

        -vvv

    """
    return '-' + flag * count if count else ''
