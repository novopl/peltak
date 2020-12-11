# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from peltak.core import context


def test_clear_removes_all_values(ctx):
    ctx.values = {
        'test1': {
            'sub': 'test value',
        }
    }

    context.clear()

    assert len(ctx.values) == 0
