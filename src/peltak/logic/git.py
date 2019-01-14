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
""" Git commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import fs
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from peltak.core import util


def add_hooks():
    # type: () -> None
    """ Add git hooks for commit and push to run linting and tests. """

    # Detect virtualenv the hooks should use

    # Detect virtualenv
    virtual_env = conf.getenv('VIRTUAL_ENV')
    if virtual_env is None:
        log.err("You are not inside a virtualenv")
        confirm_msg = (
            "Are you sure you want to use global python installation "
            "to run your git hooks? [y/N] "
        )
        click.prompt(confirm_msg, default=False)
        if not click.confirm(confirm_msg):
            log.info("Cancelling")
            return

        load_venv = ''
    else:
        load_venv = 'source "{}/bin/activate"'.format(virtual_env)

    commit_hook = conf.proj_path('.git/hooks/pre-commit')
    push_hook = conf.proj_path('.git/hooks/pre-push')

    # Write pre-commit hook
    log.info("Adding pre-commit hook <33>{}", commit_hook)
    fs.write_file(commit_hook, util.remove_indent('''
        #!/bin/bash
        PATH="/opt/local/libexec/gnubin:$PATH"
        
        {load_venv}
        
        peltak lint --commit
        
    '''.format(load_venv=load_venv)))

    # Write pre-push hook
    log.info("Adding pre-push hook: <33>{}", push_hook)
    fs.write_file(push_hook, util.remove_indent('''
        #!/bin/bash
        PATH="/opt/local/libexec/gnubin:$PATH"
        
        {load_venv}
        
        peltak test --allow-empty
        
    '''.format(load_venv=load_venv)))

    log.info("Making hooks executable")
    if not context.get('pretend', False):
        os.chmod(conf.proj_path('.git/hooks/pre-commit'), 0o755)
        os.chmod(conf.proj_path('.git/hooks/pre-push'), 0o755)


def push():
    # type: () -> None
    """ Push the current branch to origin.

    This is an equivalent of ``git push -u origin <branch>``. Mainly useful for
    the first push as afterwards ``git push`` is just quicker. Free's you from
    having to manually type the current branch name in the first push.
    """
    branch = git.current_branch().name
    shell.run('git push -u origin {}'.format(branch))
