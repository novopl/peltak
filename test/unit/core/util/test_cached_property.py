# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from unittest.mock import Mock, patch
import time
from peltak.core.util import cached_property
from datetime import datetime, timedelta


class FakeClass(object):
    def __init__(self):
        self.call_count = 0

    @cached_property(seconds=5)
    def test_prop_round(self):
        self.call_count += 1
        return None

    @cached_property(seconds=0.5)
    def test_prop_float(self):
        self.call_count += 1
        return None


def test_not_called_all_the_time():
    obj = FakeClass()

    v1 = obj.test_prop_round
    v2 = obj.test_prop_round

    assert obj.call_count == 1


def test_called_after_time_expires():
    obj = FakeClass()

    v1 = obj.test_prop_round
    with patch('peltak.core.util.datetime') as datetime_m:
        datetime_m.now.return_value = datetime.now() + timedelta(seconds=5)
        v2 = obj.test_prop_round

    assert obj.call_count == 2


def test_works_with_float_seconds():
    obj = FakeClass()

    v1 = obj.test_prop_float
    v2 = obj.test_prop_float

    assert obj.call_count == 1


def test_works_with_float_seconds_2():
    obj = FakeClass()

    v1 = obj.test_prop_float

    with patch('peltak.core.util.datetime') as datetime_m:
        datetime_m.now.return_value = datetime.now() + timedelta(seconds=0.6)
        v2 = obj.test_prop_float

    assert obj.call_count == 2
