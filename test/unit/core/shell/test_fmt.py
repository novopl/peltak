# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import patch

import pytest

from peltak.core import shell


@pytest.mark.parametrize('msg,expected', [
    ('<31>hello<0>', '\x1b[31mhello\x1b[0m'),
    ('<33>hello<0>', '\x1b[33mhello\x1b[0m'),
    ('<1>hello<0>', '\x1b[1mhello\x1b[0m'),
])
@patch('peltak.core.shell.is_tty', True)
def test_properly_converts_to_shell_opcodes_when_on_tty(msg, expected):
    assert shell.fmt(msg) == expected


@pytest.mark.parametrize('msg,expected', [
    ('<31>hello<0>', 'hello'),
    ('<33>hello<0>', 'hello'),
    ('<1>hello<0>', 'hello'),
])
@patch('peltak.core.shell.is_tty', False)
def test_removes_color_tags_when_not_on_tty(msg, expected):
    assert shell.fmt(msg) == expected


@pytest.mark.parametrize('msg,args,kw,expected', [
    ('hello {}', ['world'], {}, 'hello world'),
    ('hello {} {}', ['world'] * 2, {}, 'hello world world'),
    ('hello {world}', [], {'world': 'world'}, 'hello world'),
])
def test_formatting_works(msg, args, kw, expected):
    assert shell.fmt(msg, *args, **kw) == expected
