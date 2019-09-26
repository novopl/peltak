# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

from peltak.core import context


def test_only_one_instance_is_ever_created():
    a = context.RunContext()
    b = context.RunContext()
    assert a is b
