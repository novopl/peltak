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
""" Miscellaneous commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import exists, isdir, join
from shutil import rmtree
from typing import List

# 3rd party imports
import click
import cliform

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import fs
from peltak.core import log
from peltak.core import shell
from peltak.core import util


def clean(exclude):
    # type: (bool, List[str]) -> None
    """ Remove all unnecessary files.

    Args:
        pretend (bool):
            If set to **True**, do not delete any files, just show what would be
            deleted.
        exclude (list[str]):
            A list of path patterns to exclude from deletion.
    """
    pretend = context.get('pretend', False)
    exclude = list(exclude) + conf.get('clean.exclude', [])
    clean_patterns = conf.get('clean.patterns', [
        '*__pycache__*',
        '*.py[cod]',
        '*.swp',
    ])

    num_files = 0
    with util.timed_block() as t:
        files = fs.filtered_walk(conf.proj_path(), clean_patterns, exclude)
        for path in files:
            try:
                num_files += 1

                if not isdir(path):
                    log.info('  <91>[file] <90>{}', path)
                    not pretend and os.remove(path)
                else:
                    log.info('  <91>[dir]  <90>{}', path)
                    not pretend and rmtree(path)

            except OSError:
                log.info("<33>Failed to remove <90>{}", path)

    if pretend:
        msg = "Would delete <33>{}<32> files. Took <33>{}<32>s"
    else:
        msg = "Deleted <33>{}<32> files in <33>{}<32>s"

    log.info(msg.format(num_files, t.elapsed_s))


class InitForm(cliform.Form):
    """ Everything needed to generate initial pelconf.yaml. """
    src_dir = cliform.Field(
        'Source directory',
        default='src',
        type=str,
        help=('The root directory for all your sources. This is what you '
              'would treat as PYTHONPATH')
    )
    build_dir = cliform.Field(
        'Build directory',
        default='.build',
        type=str,
        help=('The directory where all build files should go. It will be '
              'shared as much as possible across the tools to reduce '
              'clutter')
    )
    src_path = cliform.Field(
        'Path to your main package',
        type=str,
        help=('This will be used for a lot of default values in the config '
              '(like for linting, reference docs etc.)')
    )
    version_file = cliform.Field(
        'Version file',
        type=str,
        default=lambda f: join(f['src_path'], '__init__.py'),
        help=('This will be used for a lot of default values in the config '
              '(like for linting, reference docs etc.)')
    )


def init(quick):
    # type: () -> None
    """ Create an empty pelconf.yaml from template """
    config_file = 'pelconf.yaml'
    prompt = "-- <35>{} <32>already exists. Wipe it?<0>".format(config_file)

    if exists(config_file) and not click.confirm(shell.fmt(prompt)):
        log.info("Canceled")
        return

    form = InitForm().run(quick=quick)

    log.info('Writing <35>{}'.format(config_file))
    pelconf_template = conf.load_template('pelconf.yaml')
    fs.write_file(config_file, pelconf_template.format(**form.values))


# Used in docstrings only until we drop python2 support
del List
