# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest
from mock import patch

# local imports
from peltak.core import log


@patch('peltak.core.shell.cprint')
def test_decorates_the_message(p_cprint):
    log.err('hello')

    p_cprint.assert_called_once_with('-- <31>hello<0>')


@pytest.mark.parametrize('msg,args,kw,expected', [
    ('hello {}', ['world'], {}, '-- <31>hello world<0>'),
    ('hello {} {}', ['world'] * 2, {}, '-- <31>hello world world<0>'),
    ('hello {world}', [], {'world': 'world'}, '-- <31>hello world<0>'),
])
@patch('peltak.core.shell.cprint')
def test_formatting_works(p_cprint, msg, args, kw, expected):
    log.err(msg, *args, **kw)

    p_cprint.assert_called_once_with(expected)
