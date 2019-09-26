# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys

# 3rd party imports
import pytest

# local imports
from peltak import testing
from peltak.extra.scripts.filters import cprint


@testing.patch_is_tty(True)
def test_inserts_shell_opcodes_when_is_tty():
    assert cprint('<32>hello, <35>world') == (
        'echo "\x1b[32mhello, \x1b[35mworld\x1b[0m"'
    )


@testing.patch_is_tty(False)
def test_no_colors_if_is_tty_is_False():
    assert cprint('<32>hello, <35>world') == 'echo "hello, world"'


# God knows why, pytest fails to collect those tests when running in tox on CircleCI.
# Works locally both in tox and running straight in the terminal.
# python2 support will soon be dropped, until then we can just skip it.
if sys.version_info > (3, 0):

    @pytest.mark.parametrize('arg,expected', [
        (123, 'echo "123"'),
        (124.123, 'echo "124.123"'),
        (True, 'echo "True"'),
        (None, 'echo "None"')
    ])
    @testing.patch_is_tty(False)
    def test_will_stringify_the_argument_first(arg, expected):
        assert cprint(arg) == expected

    @pytest.mark.parametrize('msg,args,kw,expected_result', [
        ('{}, {}', ['hello', 'world'], {}, 'echo "hello, world"'),
        ('{1}, {0}', ['hello', 'world'], {}, 'echo "world, hello"'),
        ('{}, {w}', ['hello'], {'w': 'world'}, 'echo "hello, world"'),
        ('{w}, {w}', [], {'h': 'hello', 'w': 'world'}, 'echo "world, world"'),
    ])
    @testing.patch_is_tty(False)
    def test_supports_formatting_directly(msg, args, kw, expected_result):
        assert cprint(msg, *args, **kw) == expected_result
