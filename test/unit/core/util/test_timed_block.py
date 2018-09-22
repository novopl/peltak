# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch, Mock

# local imports
from peltak.core import util


@patch('time.time', Mock(side_effect=[1, 2]))
def test_returns_proper_results():

    with util.timed_block() as t:
        pass

    assert t.elapsed == 1
    assert t.elapsed_ms == 1000
    assert t.elapsed_s == 1
