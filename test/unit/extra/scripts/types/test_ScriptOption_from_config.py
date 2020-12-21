# pylint: disable=missing-docstring
import pytest

from peltak.extra.scripts.types import ScriptOption


def test_works():
    opt = ScriptOption.from_config(dict(
        name=['-f', '--force'],
        about='Force the execution, will not ask any questions',
        is_flag=True,
        default=False,
        count=False,
        type='int'
    ))

    assert opt.name == ['-f', '--force']
    assert opt.about == 'Force the execution, will not ask any questions'
    assert opt.default is False
    assert opt.is_flag is True
    assert opt.count is False
    assert opt.type is int


def test_works_with_only_name():
    opt = ScriptOption.from_config({'name': '--force'})

    assert opt.name == ['--force']
    assert opt.about == ''
    assert opt.default is None
    assert opt.is_flag is False
    assert opt.count is False
    assert opt.type is str


def test_raises_ValueError_if_type_is_not_supported():
    with pytest.raises(ValueError):
        ScriptOption.from_config({'name': '--test', 'type': 'XXXX'})


def test_raises_ValueError_if_name_is_not_defined():
    with pytest.raises(ValueError):
        ScriptOption.from_config({})


@pytest.mark.parametrize('name', (None, [], ''))
def test_raises_ValueError_if_name_is_empty(name):
    with pytest.raises(ValueError):
        ScriptOption.from_config(dict(name=name))


def test_supports_passing_the_name_as_string():
    opt = ScriptOption.from_config(dict(name='--force'))

    assert opt.name == ['--force']
