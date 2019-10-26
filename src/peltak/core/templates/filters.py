# -*- coding: utf-8 -*-
"""
.. module:: peltak.core.templates.filters
    :synopsis: Built-in script template filters

################################
Built-in script template filters
################################

Built-in jinja2 filters
=======================

You can find the list of all filters built into jinja2 in `jinja2 documentation`_

Filters provided by peltak
==========================

.. autofunction:: header
.. autofunction:: count_flag
.. autofunction:: cprint
.. autofunction:: wrap_paths


.. _jinja2 documentation:
    https://jinja.palletsprojects.com/en/2.10.x/templates/#list-of-builtin-filters

"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any

# 3rd party imports
from six import string_types

# local imports
from peltak.core import fs
from peltak.core import shell


def header(title):
    # type: (Any) -> str
    """ Converts a given title into a pretty header with colors.

    **Usage:**

    .. code-block:: jinja

        {{ 'hello' | header }}

    will result in::

        = hello ================================================================

    The resulting string will be colored for printing in the terminal.
    """
    title = str(title)
    if (len(title) > 72):
        title = title[0:70] + '...'

    remaining = 80 - len(title) - 3
    return shell.fmt('echo "<32>= <35>{title} <32>{bar}<0>"',
                     title=title,
                     bar='=' * remaining)


def count_flag(count, flag):
    # type: (int, str) -> str
    """ Returns the given flag letter as a count flag.

    **Usage:**

    .. code-block:: jinja

        {{ set verbose = 3 }}
        {{ verbose | count_flag('v') }}

    will result in::

        -vvv

    In the above example, if ``verbose`` is ``0`` the result of this filter will
    be an empty string.
    """
    if not isinstance(count, int) or count < 0:
        raise ValueError('Cannot create count flag from count={}'.format(count))

    if not isinstance(flag, string_types):
        raise ValueError("Flags must be strings, got: {}".format(flag))

    if len(flag) > 1:
        raise ValueError("Flags must have length 1, got: {}".format(flag))

    if not flag.isalpha():
        raise ValueError("Flags must be letters, got: {}".format(flag))

    return '-' + flag * count if count else ''


def cprint(msg, *args, **kw):
    """ Will convert the given message to an echo statement with color opcodes.

    This supports the same syntax as `peltak.core.shell.fmt` (used internally here).
    The color processing will replace any tag like object in format ``<NUMBER>``
    into a corresponding opcode. Here's a quick cheatsheet on some of the more
    usefull opcodes

    ========== =================================================================
     Tag        Description
    ---------- -----------------------------------------------------------------
     ``<0>``    Reset all formatting to default values.
     ``<1>``    Intensify current color (will affect all other color opcodes).
     ``<31>``   Set text color to red.
     ``<32>``   Set text color to green.
     ``<33>``   Set text color to yellow.
     ``<34>``   Set text color to blue.
     ``<35>``   Set text color to pink.
     ``<35>``   Set text color to teal.
    ========== =================================================================

    **Usage:**

    .. code-block:: jinja

        {{ '<35>hello, <32>world' | cprint }}

    will result in the following::

        echo "\\x1b[35mhello, \\x1b[32mworld\\x1b[0m"

    Which inside a terminal will be rendered as *hello* in ping and world in
    green.

    **cprint** also supports formatting, same as in the built-in ``format()``
    function.

    .. code-block:: jinja

        {{ "hello, {}, I'm {name}" | cprint('Susan', name='John') }}

    will result in::

        echo "hello, Susan, I'm John\\x1b[0m"

    """
    return shell.fmt('echo "{}<0>"', str(msg).format(*args, **kw))


def wrap_paths(paths):
    """ Returns a string with all items wrapped in quotes and separated by space.

    **Usage:**

    .. code-block:: jinja

        {% set paths = ['file 1', 'file 2', 'file 3'] %}
        cp {{ paths | wrap_paths }} out_dir/

    will result in::

        cp "file 1" "file 2" "file 3" out_dir/

    """
    return fs.wrap_paths(paths)


# Used only in type hint comments
del Any
