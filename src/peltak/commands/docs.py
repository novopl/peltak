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
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import

# local imports
from peltak.core import conf
from . import root_cli, click, pretend_option, verbose_option


conf.command_requirements(
    'sphinx-refdoc~=0.3.0',
    'sphinx-rtd-theme~=0.2'
)


@root_cli.group('docs', invoke_without_command=True)
@click.option(
    '--recreate',
    is_flag=True,
    help="Delete build and out directories before running."
)
@click.option(
    '--gen-index',
    is_flag=True,
    help="Generate main index for code reference"
)
@click.option(
    '--run-doctests',
    is_flag=True,
    help="Generate main index for code reference"
)
@pretend_option
@verbose_option
@click.pass_context
def docs_cli(ctx, recreate, gen_index, run_doctests):
    # type: (click.Context, bool, bool, bool) -> None
    """ Build project documentation.

    This command will run sphinx-refdoc first to generate the reference
    documentation for the code base. Then it will run sphinx to generate the
    final docs. You can configure the directory that stores the docs source
    (index.rst, conf.py, etc.) using the DOC_SRC_PATH conf variable. In case you
    need it, the sphinx build directory is located in ``BUILD_DIR/docs``.

    The reference documentation will be generated for all directories listed
    under 'REFDOC_PATHS conf variable. By default it is empty so no reference
    docs are generated.

    Sample Config::

        \b
        build_dir: '.build'

        docs:
          path: 'docs'
          reference:
            - 'src/mypkg'

    Examples::

        \b
        $ peltak docs                           # Generate docs for the project
        $ peltak docs --no-index                # Skip main reference index
        $ peltak docs --recreate --no-index     # Build docs from clean slate

    """
    if ctx.invoked_subcommand:
        return

    from peltak.logic import docs
    docs.docs(recreate, gen_index, run_doctests)
