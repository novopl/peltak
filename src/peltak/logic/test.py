# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" Test command implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import itertools
import sys
import os.path
from typing import Any, Dict, List, Text

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import log
from peltak.core import fs
from peltak.core import shell


DEFAULT_PYTEST_CFG = 'ops/tools/pytest.ini'
DEFAULT_COVERAGE_CFG = 'ops/tools/coverage.ini'


class TestsError(Exception):
    """ Base class for exceptions raised by this test runner. """


class TestsNotConfigured(Exception):
    """ Raised when the configuration is missing and can't be guessed. """
    def __init__(self):
        # type: () -> None
        super(TestsNotConfigured, self).__init__(
            "No tests detected. Configure `test.types` in your pelconf.yaml."
            "Use `peltak test --help` for more information."
        )


def test(tests_type,    # type: Text
         junit,         # type: bool
         show_locals,   # type: bool
         no_coverage,   # type: bool
         plugins,       # type: Text
         allow_empty    # type: bool
         ):
    # type: (...) -> None
    """ Run tests using pytest

    Args:
        tests_type (str):
            Tests type to run. The types are defined in the project
            configuration.
        junit (bool):
            If **True** it will save junit test report in build directory.
        show_locals (bool):
            Show the value of locals.
        no_coverage (bool):
            Do not generate coverage report
        plugins (str):
            Comma separated list of pytest plugins to enable/disable. If the
            plugin name is prefixed with '-' sign the plugin will be disabled.
        allow_empty (bool):
            If set to **False** it will return non-zero code if the test suite
            is empty.
    """
    build_dir = conf.get_path('build_dir', '.build')
    src_dir = conf.get_path('src_dir')
    src_path = conf.get_path('src_path')
    pytest_cfg = conf.get_path('test.pytest_cfg', DEFAULT_PYTEST_CFG)
    coverage_cfg = conf.get_path('test.coverage_cfg_path', DEFAULT_COVERAGE_CFG)

    try:
        test_config = get_test_config_by_type(tests_type)
        test_paths = test_config['paths'] or []
        test_paths = [conf.proj_path(p) for p in test_paths]

        args = list(itertools.chain(
            ['-c ' + pytest_cfg],
            args_verbosity(context.get('verbose', 0), show_locals),
            args_coverage(not no_coverage, build_dir, src_path, coverage_cfg),
            args_junit(junit, build_dir),
            args_plugins(plugins.split(',')),
            args_django(
                '-django' not in plugins,
                django_settings=conf.get('django_settings', None),
                django_settings_test=conf.get('django_test_settings', None)
            )
        ))

        result = shell.run(
            'pytest {args} {paths}'.format(
                args=' '.join(args),
                paths=fs.wrap_paths(test_paths)
            ),
            env={'PYTHONPATH': src_dir},
            exit_on_error=False
        )

        log.info("<1>HTML report:<0> <34>file://{}".format(
            conf.proj_path(build_dir, 'coverage', 'index.html')
        ))

        retcode = result.return_code
        # 4 - file not found (missing directory etc.)
        # 5 - no tests found
        if retcode and not (allow_empty is True and retcode in (4, 5)):
            sys.exit(result.return_code)

    except TestsError:
        sys.exit(1)


def args_coverage(enabled, build_dir, src_path, config):
    # type: (bool, Text, Text, Text) -> List[Text]
    """ Build pytest args for code coverage.

    Args:
        enabled (bool):
            Whether the coverage generation should be enabled. Sometimes
            debugging doesn't work properly when coverage is enabled.
        build_dir (str):
            Build directory. The coverage report will go to a 'coverage'
            subdirectory inside this dir.
        src_path (str):
            Path to the source directory. This will be used as the path to the
            covered code
        config (str):
            Path to the coverage configuration.

    Returns:
        list[str]: The list of pytest arguments. Can be joined on ' ' to make
            them ready to be appended to the pytest command.
    """
    if not enabled:
        return []

    return [
        '--cov-config={}'.format(config),
        '--cov={}'.format(src_path),
        '--cov-report=term',
        '--cov-report=html:{}'.format(os.path.join(build_dir, 'coverage')),
    ]


def args_junit(enabled, build_dir):
    # type: (bool, Text) -> List[Text]
    """ Build pytest args jUnit report generation.

    Args:
        enabled (bool):
            Whether the junit report generation should be enabled.
        build_dir (str):
            Build directory. The coverage report will go to a 'coverage'
            subdirectory inside this dir.

    Returns:
        list[str]: The list of pytest arguments. Can be joined on ' ' to make
            them ready to be appended to the pytest command.
    """
    if not enabled:
        return []

    junit_report = os.path.join(build_dir, 'test-results.xml')
    return ['--junitxml='.format(junit_report)]


def args_django(enabled, django_settings, django_settings_test):
    # type: (bool, Text, Text) -> List[Text]
    """ Build pytest args for django support.

    Args:
        enabled (bool):
            Whether the django support should be enabled.
        django_settings (str):
            Django settings module, same as ``DJANGO_SETTINGS_MODULE`` env
            variable used by django.
        django_settings_test (str):
            Django settings module for tests. Test runner can use a different
            django settings module than the project configuration. If not given
            and **django_settings** was, then **django_settings** will be used.

    Returns:
        list[str]: The list of pytest arguments. Can be joined on ' ' to make
            them ready to be appended to the pytest command.
    """
    if not enabled:
        return []

    args = []
    if django_settings_test is not None:
        args += ['--ds {}'.format(django_settings_test)]
    elif django_settings is not None:
        args += ['--ds {}'.format(django_settings)]

    return args


def args_plugins(plugins):
    # type: (List[Text]) -> List[Text]
    """ Build pytest args to configure plugins.

    Args:
        plugins (list[str]:
            A list of plugins that should be enabled/disabled. If the name of
            the plugin is prefixed with ``-``, then it will be disabled,
            otherwise it will be enabled.

    Returns:
        list[str]: The list of pytest arguments. Can be joined on ' ' to make
            them ready to be appended to the pytest command.
    """
    args = []

    for plug_name in (plugins or []):
        if not plug_name.strip():
            continue

        if plug_name.startswith('-'):
            args += ['-p no:{}'.format(plug_name[1:])]
        else:
            args += ['-p {}'.format(plug_name)]

    return args


def args_verbosity(level, show_locals):
    # type: (int, bool) -> List[Text]
    """ Build pytest args to configure the output verbosity.

    Args:
        level (int):
            Verbosity level. This translates directly to the ``-v`` flag in
            **pytest**.
        show_locals (bool):
            If set to **True**, the stack traces will also include values for
            local variables. Useful for CI test runs for investigation if
            something goes wrong. Locally its usually easier to use the
            debugger.

    Returns:
        list[str]: The list of pytest arguments. Can be joined on ' ' to make
            them ready to be appended to the pytest command.
    """
    args = []

    if level >= 1:
        args += ['-' + 'v' * level]
    if level >= 2:
        args += ['--full-trace']

    if show_locals:
        args += ['-l']

    return args


def get_test_config_by_type(tests_type):
    # type: (Text) -> Dict[Text, Any]
    """ Get the test configuration for the given test type.

    Args:
        tests_type (str):
            The type of tests we want the configuration for.

    Returns:
        dict[str, Any]: The test configuration for the given test type.

    Raises:
        TestsNotConfigured: when the configuration is missing and can't be
            guessed.
    """
    test_types = conf.get('test.types', {})
    test_config = test_types.get(tests_type)

    if test_config is not None:
        return test_config

    log.info("Test configuration '{}' missing, trying to guess", tests_type)
    possible_test_paths = (
        conf.proj_path('test'),
        conf.proj_path('tests'),
    )

    for path in possible_test_paths:
        if os.path.exists(path):
            return {'paths': [path]}

    raise TestsNotConfigured()


# Used in type hint comments only (until we drop python2 support)
del Any, Dict, List, Text
