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
""" CLI definition. """
from __future__ import absolute_import

from peltak.commands import root_cli, click


@root_cli.group('changelog', invoke_without_command=True)
@click.pass_context
def changelog_cli(ctx):
    # type: () -> None
    """ Generate changelog from commit messages. """
    if ctx.invoked_subcommand:
        return

    from peltak.core import shell
    from . import logic
    shell.cprint(logic.changelog())
