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
""" Documentation commands implementation. """
from __future__ import absolute_import, unicode_literals, print_function

# stdlib imports
import os.path
import shutil
import sys

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import log
from peltak.core import shell
from peltak.core import util


def docs(recreate, gen_index, run_doctests):
    # type: (bool, bool, bool) -> None
    """ Build the documentation for the project.

    Args:
        recreate (bool):
            If set to **True**, the build and output directories will be cleared
            prior to generating the docs.
        gen_index (bool):
            If set to **True**, it will generate top-level index file for the
            reference documentation.
        run_doctests (bool):
            Set to **True** if you want to run doctests after the documentation
            is generated.
        pretend (bool):
            If set to **True**, do not actually execute any shell commands, just
            print the command that would be executed.
    """
    build_dir = conf.get_path('build_dir', '.build')
    docs_dir = conf.get_path('docs.path', 'docs')
    refdoc_paths = conf.get('docs.reference', [])

    docs_html_dir = conf.get_path('docs.out', os.path.join(docs_dir, 'html'))
    docs_tests_dir = conf.get_path('docs.tests_out',
                                   os.path.join(docs_dir, 'doctest'))
    docs_build_dir = os.path.join(build_dir, 'docs')

    if recreate:
        for path in (docs_html_dir, docs_build_dir):
            if os.path.exists(path):
                log.info("<91>Deleting <94>{}".format(path))
                shutil.rmtree(path)

    if refdoc_paths:
        gen_ref_docs(gen_index)
    else:
        log.err('Not generating any reference documentation - '
                'No docs.reference specified in config')

    with conf.within_proj_dir(docs_dir):
        log.info('Building docs')
        shell.run('sphinx-build -b html -d {build} {docs} {out}'.format(
            build=docs_build_dir,
            docs=docs_dir,
            out=docs_html_dir,
        ))

        if run_doctests:
            log.info('Running doctests')
            shell.run('sphinx-build -b doctest -d {build} {docs} {out}'.format(
                build=docs_build_dir,
                docs=docs_dir,
                out=docs_tests_dir,
            ))

        log.info('You can view the docs by browsing to <34>file://{}'.format(
            os.path.join(docs_html_dir, 'index.html')
        ))


def gen_ref_docs(gen_index=False):
    # type: (int, bool) -> None
    """ Generate reference documentation for the project.

    This will use **sphinx-refdoc** to generate the source .rst files for the
    reference documentation.

    Args:
        gen_index (bool):
            Set it to **True** if you want to generate the index file with the
            list of top-level packages. This is set to default as in most cases
            you only have one package per project so you can link directly to
            that package reference (and if index were generated sphinx would
            complain about file not included in toctree).
    """
    try:
        from refdoc import generate_docs
    except ImportError as ex:
        msg = ("You need to install sphinx-refdoc if you want to generate "
               "code reference docs.")

        print(msg, file=sys.stderr)
        log.err("Exception: {}".format(ex))
        sys.exit(-1)

    pretend = context.get('pretend', False)

    docs_dir = conf.get_path('docs.path', 'docs')
    docs_ref_dir = os.path.join(docs_dir, 'ref')
    refdoc_paths = conf.get('docs.reference', [])

    if os.path.exists(docs_ref_dir):
        if not pretend:
            log.info('Removing existing reference docs')
            shutil.rmtree(docs_ref_dir)
        else:
            log.info('Would remove old reference docs')

    args = {
        'out_dir': docs_ref_dir,
        'verbose': context.get('verbose', 0),
    }

    if gen_index:
        args['gen_index'] = True

    pkg_paths = [conf.proj_path(p) for p in refdoc_paths]

    if not pretend:
        log.info('Generating reference documentation')
        generate_docs(pkg_paths, **args)
    else:
        log.info("Would generate reference docs with the following params")
        shell.cprint('<90>{}', util.yaml_dump(args).rstrip())
        shell.cprint('<90>paths:\n<34>{}', util.yaml_dump(pkg_paths).rstrip())
