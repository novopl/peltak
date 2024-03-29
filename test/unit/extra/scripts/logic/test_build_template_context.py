# pylint: disable=missing-docstring
import dataclasses
from unittest.mock import Mock, patch

from peltak import testing
from peltak.core import conf
from peltak.core.context import RunContext
from peltak.core.scripts.logic import build_template_context
from peltak.core.scripts.types import Script


@testing.patch_pelconf({'cfg': {'pelconf': 'hello'}})
def test_works():
    options = {'fake_opt': 'hello'}
    script = Script.from_config('test', {'command': 'fake-cmd'})

    RunContext().set('verbose', 3)
    RunContext().set('pretend', False)

    result = build_template_context(script, options)

    assert result['ctx'] == RunContext().values
    assert result['conf'] == {'pelconf': 'hello'}
    assert result['proj_path'] == conf.proj_path
    assert result['script'] == dataclasses.asdict(script)
    assert result['opts'] == {
        'verbose': 3,
        'pretend': False,
        'fake_opt': 'hello',
    }
    assert 'files' not in result


@patch('peltak.core.fs.collect_files', Mock(return_value=[
    'file1',
    'file2',
    'file3'
]))
@testing.patch_pelconf({'cfg': {'pelconf': 'hello'}})
def test_includes_files_if_specified_in_config():
    options = {'fake_opt': 'hello'}
    script = Script.from_config('test', {
        'command': 'fake-cmd',
        'files': {
            'paths': 'fake_path'
        },
    })

    RunContext().set('verbose', 3)
    RunContext().set('pretend', False)

    result = build_template_context(script, options)
    assert 'files' in result
    assert result['files'] == ['file1', 'file2', 'file3']

    RunContext().set('verbose', 0)
