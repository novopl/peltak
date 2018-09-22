# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import conf


def test_initialized_values_are_available():
    conf.init({'fake': 'value'})

    assert conf.get('fake') == 'value'


def test_overwrites_the_existing_config():
    conf.init({'fake1': 'value1'})
    conf.init({'fake2': 'value2'})

    assert conf.get('fake2') == 'value2'
    with pytest.raises(AttributeError):
        conf.get('fake1')
