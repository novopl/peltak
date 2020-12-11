# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from peltak.core import context


def test_only_one_instance_is_ever_created():
    a = context.RunContext()
    b = context.RunContext()
    assert a is b
