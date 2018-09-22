# -*- coding: utf-8 -*-
""" Test command implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
import os.path

# local imports
from peltak.core import conf
from peltak.core import log
from peltak.core import fs
from peltak.core import shell


def test(tests_type,
         verbose,
         junit,
         no_locals,
         no_coverage,
         plugins,
         allow_empty):
    """ Run tests using pytest

    :param str tests_type:
        Tests type to run. The types are defined in the project configuration.
    :param int verbose:
        Verbosity level (0-3)
    :param bool junit:
        If **True** it will save junit test report in build directory.
    :param bool no_locals:
        Do not show locals
    :param bool no_coverage:
        Do not generate coverage report
    :param List[str] plugins:
        List of pytest plugins to enable/disable. If the plugin name is prefixed
        with '-' sign the plugin will be disabled.
    :param bool allow_empty:
        If set to **False** it will return non-zero code if the test suite is
        empty.
    """
    log.info("Running <33>{} <32>tests".format(tests_type))

    build_dir = conf.get_path('build_dir', '.build')

    pytest_cfg_path = conf.get_path('test.pytest_cfg', 'ops/tools/pytest.ini')
    test_types = conf.get('test.types', {})

    coverage_out_path = os.path.join(build_dir, 'coverage')
    coverage_cfg_path = conf.get_path('coverage_cfg_path',
                                      'ops/tools/coverage.ini')

    django_settings = conf.get('django_settings', None)
    django_test_settings = conf.get('django_test_settings', None)

    src_dir = conf.get_path('src_dir')
    src_path = conf.get_path('src_path')
    plugins = plugins.split(',')
    args = []

    if not no_coverage:
        args += [
            '--cov-config={}'.format(coverage_cfg_path),
            '--cov={}'.format(src_path),
            '--cov-report=term',
            '--cov-report=html:{}'.format(coverage_out_path),
        ]

    if junit:
        args += ['--junitxml={}/test-results.xml'.format('.build')]

    if '-django' not in plugins:
        if django_test_settings is not None:
            args += ['--ds {}'.format(django_test_settings)]
        elif django_settings is not None:
            args += ['--ds {}'.format(django_settings)]

    if verbose >= 1:
        args += ['-' + 'v' * verbose]
    if verbose >= 2:
        args += ['--full-trace']

    if not no_locals:
        args += ['-l']

    if plugins:
        for plug_name in plugins:
            if not plug_name.strip():
                continue

            if plug_name.startswith('-'):
                args += ['-p no:{}'.format(plug_name[1:])]
            else:
                args += ['-p {}'.format(plug_name)]

    test_config = test_types.get(tests_type)
    if test_config is None:
        log.info("Test type configuration missing: '{}'".format(src_path))

        for possible_path in (conf.proj_path('test'), conf.proj_path('tests')):
            if os.path.exists(possible_path):
                test_config = {'paths': possible_path}
                break
        else:
            log.err("No tests detected. Configure your TEST_TYPES.")
            sys.exit(-1)

    mark = test_config.get('mark')

    if mark:
        args += ['-m "{}"'.format(mark)]

    test_paths = test_config['paths'] or []
    test_paths = [conf.proj_path(p) for p in test_paths]
    result = shell.run(
        'pytest -c {conf} {args} {paths}'.format(
            conf=pytest_cfg_path,
            args=' '.join(args),
            paths=fs.surround_paths_with_quotes(test_paths)
        ),
        env={'PYTHONPATH': src_dir},
        exit_on_error=False
    )

    log.info("To see the HTML coverage report browse to <34>file://{}".format(
        conf.proj_path('.build/coverage/index.html')
    ))

    if result.failed and not (allow_empty is True and result.return_code == 5):
        sys.exit(result.return_code)
