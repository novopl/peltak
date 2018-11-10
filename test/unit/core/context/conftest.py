# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import context


@pytest.fixture()
def ctx():
    old = context.GlobalContext().values
    context.clear()

    yield context.GlobalContext()

    context.GlobalContext().values = old
