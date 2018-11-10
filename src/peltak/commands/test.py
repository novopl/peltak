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
"""
Testing commands
"""
from __future__ import absolute_import

from peltak.core import conf
from . import root_cli, click, pretend_option, verbose_option


conf.command_requirements(
    'coverage~=4.5',
    'factory-boy~=2.11',
    'mock==2.0.0',
    'pytest~=3.7',
    'pytest-cov==2.5.1',
    'pytest-sugar~=0.9'
)


@root_cli.group('test', invoke_without_command=True)
@click.argument('tests_type', metavar='<type>', type=str, default='default')
@click.option(
    '--junit',
    is_flag=True,
    help="Write junit XML report to build_dir/test-results.xml."
)
@click.option(
    '--no-locals',
    is_flag=True,
    help="Disable pytest printing the values of local variables."
)
@click.option(
    '--no-coverage',
    is_flag=True,
    help="Disable code coverage generation."
)
@click.option(
    '--allow-empty',
    is_flag=True,
    help="Do not return non-zero code if the test suite is empty."
)
@click.option(
    '--plugins',
    type=str,
    default='',
    help=("Comma separated list of pytest plugins to activate. If the name "
          "of the plugins starts with '-' it will be disabled, otherwise it "
          "will be enabled.")
)
@pretend_option
@verbose_option
@click.pass_context
def test_cli(ctx, tests_type, junit, no_locals, no_coverage, plugins,
             allow_empty):
    # type: (click.Context, str, bool, bool, bool, str, bool) -> None
    """ Run tests against the current python version.

    This command uses pytest internally and is just a thing wrapper over it
    to simplify most common tasks. You can define multiple test types where
    a test type is a combination of paths to test and pytest marker definition
    for the test run. This allows to split tests with fine granularity and
    and run them easily. You need at least one test type to run the tests. The
    test type *default* will be used as default if no type is specified. If
    there is no configuration for *default* it will run the tests in the
    directory specified by SRC_PATH conf variable.

    src_dir is used as PYTHONPATH for the test runner. If you need to customize
    it, use that variable.

    The coverage report will be written to ``build_dir/coverage``.

    If your project is using django, you can use django_test_settings conf
    variable to specify which settings to use for the tests.

    Example Configuration::

        \b
        test:
          coverage_cfg_path: 'ops/tools/coverage',
          django_test_settings: 'mypkg.settings.test',
          types:
            default:
                paths: ['test']
            no_django:
                paths: ['test']
                mark: 'not django'

    Examples:

        \b
        $ peltak test                   # Run tests using the default options
        $ peltak test --no-sugar        # Disable pretty output
        $ peltak test --junit           # Generate build_dir/test-results.xml
        $ peltak test --no-sugar -vv    # Be extra verbose

    """
    if ctx.invoked_subcommand:
        return

    from peltak.logic import test
    test.test(
        tests_type,
        junit,
        not no_locals,
        no_coverage,
        plugins,
        allow_empty
    )
