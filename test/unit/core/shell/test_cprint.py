# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak.core import shell


@pytest.mark.parametrize('msg,expected', [
    ('<31>hello', '<31>hello<0>'),
    ('<33>hello<0>', '<33>hello<0><0>'),
])
@patch('peltak.core.shell.is_tty', True)
@patch('peltak.core.shell.fmt')
@patch('peltak.core.shell.print', Mock())
def test_clears_formatting_at_the_end_of_each_call(p_fmt, msg, expected):
    shell.cprint(msg)

    p_fmt.assert_called_once_with(expected)


@pytest.mark.parametrize('msg,args,kw,expected', [
    ('hello {}', ['world'], {}, 'hello world<0>'),
    ('hello {} {}', ['world'] * 2, {}, 'hello world world<0>'),
    ('hello {world}', [], {'world': 'world'}, 'hello world<0>'),
])
@patch('peltak.core.shell.fmt')
@patch('peltak.core.shell.print', Mock())
def test_formatting_works(p_fmt, msg, args, kw, expected):
    shell.cprint(msg, *args, **kw)

    p_fmt.assert_called_once_with(expected)
