# -*- coding: utf-8 -*-
""" Documentation commands implementation. """
from __future__ import absolute_import, unicode_literals, print_function

# stdlib imports
import os.path
import shutil
import sys

# local imports
from peltak.core import conf
from peltak.core import log
from peltak.core import shell


def docs(recreate, gen_index, run_doctests, verbose):
    """ Build the documentation for the project.

    :param bool recreate:
        If set to **True**, the build and output directories will be cleared
        prior to generating the docs.
    :param bool gen_index:
        If set to **True**, it will generate top-level index file for the
        reference documentation.
    """
    build_dir = conf.get_path('build_dir', '.build')
    docs_dir = conf.get_path('docs.path', 'docs')
    refdoc_paths = conf.get('docs.reference', [])

    docs_html_dir = os.path.join(docs_dir, 'html')
    docs_tests_dir = os.path.join(docs_dir, 'doctest')
    docs_ref_dir = os.path.join(docs_dir, 'ref')
    docs_build_dir = os.path.join(build_dir, 'docs')

    if recreate:
        for path in (docs_html_dir, docs_build_dir):
            if os.path.exists(path):
                log.info("<91>Deleting <94>{}".format(path))
                shutil.rmtree(path)

    if refdoc_paths:
        _gen_ref_docs(docs_ref_dir, verbose, gen_index)
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


def _gen_ref_docs(ref_path, verbose, gen_index=False):
    try:
        from refdoc import generate_docs as _generate_docs
    except ImportError as ex:
        msg = ("You need to install sphinx-refdoc if you want to generate "
               "code reference docs.")

        print(msg, file=sys.stderr)
        log.err("Exception: {}".format(ex))
        sys.exit(-1)

    refdoc_paths = conf.get('docs.reference', [])

    log.info('Removing previously generated reference documentation')
    if os.path.exists(ref_path):
        shutil.rmtree(ref_path)

    log.info('Generating reference documentation')
    args = {
        'out_dir': ref_path,
        'verbose': verbose,
    }

    if gen_index:
        args['gen_index'] = True

    pkg_paths = [conf.proj_path(p) for p in refdoc_paths]

    _generate_docs(pkg_paths, **args)
