# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import pytest

from peltak.core import context


@pytest.fixture()
def ctx():
    old = context.RunContext().values
    context.clear()

    yield context.RunContext()

    context.RunContext().values = old
