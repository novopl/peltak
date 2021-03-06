# pylint: disable=missing-docstring
import pytest

from peltak.core import context


@pytest.fixture()
def ctx():
    old = context.RunContext().values
    context.clear()

    yield context.RunContext()

    context.RunContext().values = old


def test_can_set_root_value(ctx):
    context.set('test', 'value')

    assert ctx.get('test') == 'value'


def test_can_set_sub_value(ctx):
    context.set('test.sub', 'value')

    assert ctx.get('test.sub') == 'value'


def test_raises_InvalidPath_if_part_of_the_path_is_not_a_dict(ctx):
    context.set('test', 'value')

    with pytest.raises(context.InvalidPath):
        context.set('test.sub', 'value')

    with pytest.raises(context.InvalidPath):
        context.set('test.sub.sub', 'value')

    del ctx     # avoid unused-variable
