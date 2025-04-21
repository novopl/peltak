# pylint: disable=missing-docstring
from unittest.mock import patch

import pytest

from peltak.core import log


@patch('peltak.core.shell.fmt')
def test_decorates_the_message(p_fmt):
    p_fmt.return_value = ''

    log.err('hello')

    p_fmt.assert_called_once_with('-- <31>hello<0>\n')


@pytest.mark.parametrize('msg,args,kw,expected', [
    ('hello {}', ['world'], {}, '-- <31>hello world<0>\n'),
    ('hello {} {}', ['world'] * 2, {}, '-- <31>hello world world<0>\n'),
    ('hello {world}', [], {'world': 'world'}, '-- <31>hello world<0>\n'),
])
@patch('peltak.core.shell.fmt')
def test_formatting_works(p_fmt, msg, args, kw, expected):
    p_fmt.return_value = ''

    log.err(msg, *args, **kw)

    p_fmt.assert_called_once_with(expected)
