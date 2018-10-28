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
    # type: (bool, bool, bool, int) -> None
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
        verbose (int):
            The verbosity level.
    """
    build_dir = conf.get_path('build_dir', '.build')
    docs_dir = conf.get_path('docs.path', 'docs')
    refdoc_paths = conf.get('docs.reference', [])

    docs_html_dir = os.path.join(docs_dir, 'html')
    docs_tests_dir = os.path.join(docs_dir, 'doctest')
    docs_build_dir = os.path.join(build_dir, 'docs')

    if recreate:
        for path in (docs_html_dir, docs_build_dir):
            if os.path.exists(path):
                log.info("<91>Deleting <94>{}".format(path))
                shutil.rmtree(path)

    if refdoc_paths:
        gen_ref_docs(verbose, gen_index)
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


def gen_ref_docs(verbose, gen_index=False):
    # type: (int, bool) -> None
    """ Generate reference documentation for the project.

    This will use **sphinx-refdoc** to generate the source .rst files for the
    reference documentation.

    Args:

        verbose (int):
            Verbosity level. This will be passed directly to sphinx-refdoc.
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

    docs_dir = conf.get_path('docs.path', 'docs')
    docs_ref_dir = os.path.join(docs_dir, 'ref')
    refdoc_paths = conf.get('docs.reference', [])

    log.info('Removing previously generated reference documentation')
    if os.path.exists(docs_ref_dir):
        shutil.rmtree(docs_ref_dir)

    log.info('Generating reference documentation')
    args = {
        'out_dir': docs_ref_dir,
        'verbose': verbose,
    }

    if gen_index:
        args['gen_index'] = True

    pkg_paths = [conf.proj_path(p) for p in refdoc_paths]

    generate_docs(pkg_paths, **args)
