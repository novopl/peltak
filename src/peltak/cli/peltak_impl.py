# Copyright 2017-2020 Mateusz Klos
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
import os
from os.path import exists, isdir
from shutil import rmtree
from typing import List

import click

import cliform
from peltak.core import conf, context, fs, log, shell, templates, util


def clean(exclude: List[str]):
    """ Remove all unnecessary files.

    Args:
        exclude (list[str]):
            A list of path patterns to exclude from deletion.
    """
    pretend = context.get('pretend', False)
    exclude = list(exclude) + conf.get('clean.exclude', [])
    clean_patterns = conf.get('clean.patterns', [
        '*__pycache__*',
        '*.py[cod]',
        '*.swp',
        "*.mypy_cache",
        "*.pytest_cache",
        "*.build",
    ])

    if log.get_verbosity() > 0:
        log.info('Clean patterns:')
        for pattern in clean_patterns:
            log.info(f'  <90>{pattern}')

        log.info('Exclude:')
        for pattern in exclude:
            log.info(f'  <90>{pattern}')

    num_files = 0
    with util.timed_block() as t:
        files = fs.filtered_walk(conf.proj_path(), clean_patterns, exclude)
        log.info('')
        log.info('Deleting:')
        for path in files:
            try:
                num_files += 1

                if not isdir(path):
                    log.info('  <91>[file] <90>{}', path)
                    if not pretend:
                        os.remove(path)
                else:
                    log.info('  <91>[dir]  <90>{}', path)
                    if not pretend:
                        rmtree(path)

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
        default='.',
        type=str,
        help=('The root directory for all your sources. This is what you '
              'would treat as PYTHONPATH')
    )
    version_file = cliform.Field(
        'Version file',
        type=str,
        default='',
        help=('This will be used for a lot of default values in the config '
              '(like for linting, reference docs etc.)')
    )


def init(quick: bool, blank: bool, force: bool, template: str):
    """ Create an empty pelconf.yaml from template """
    config_file = 'pelconf.yaml'
    template_file = 'peltak-py.yaml' if template == 'py' else 'peltak-js.yaml'
    prompt = "-- <35>{} <32>already exists. Wipe it?<0>".format(config_file)

    if not force and exists(config_file) and not click.confirm(shell.fmt(prompt)):
        log.info("Canceled")
        return

    ctx = dict(blank=blank)

    if not blank:
        form = InitForm().run(quick=quick)
        ctx.update(form.values)

    config_content = templates.Engine().render_file(template_file, ctx)

    log.info('Writing <35>{}'.format(config_file))
    fs.write_file(config_file, config_content)

    if log.get_verbosity() > 0:
        print(f"{'- ' * 40}\n{shell.highlight(config_content, 'yaml')}{'- ' * 40}")
