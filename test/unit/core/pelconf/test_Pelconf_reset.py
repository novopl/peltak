# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import pytest

from peltak.core import conf


def test_initialized_values_are_available():
    conf.reset({'fake': 'value'})

    assert conf.get('fake') == 'value'


def test_overwrites_the_existing_config():
    conf.reset({'fake1': 'value1'})
    conf.reset({'fake2': 'value2'})

    assert conf.get('fake2') == 'value2'
    with pytest.raises(AttributeError):
        conf.get('fake1')
