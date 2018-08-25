# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import, print_function
from . import cli, click


@cli.command()
@click.option('--recreate', is_flag=True)
@click.option('--no-index', is_flag=True)
def docs(recreate=False, no_index=False):
    """ Build project documentation. """
    import os.path
    import shutil
    from peltak.core import conf
    from peltak.core import log
    from peltak.core import shell

    build_dir = conf.get_path('BUILD_DIR', '.build')
    docs_src_path = conf.get_path('DOC_SRC_PATHS', 'docs')
    refdoc_paths = conf.get('REFDOC_PATHS', [])

    docs_out_path = os.path.join(docs_src_path, 'html')
    docs_ref_path = os.path.join(docs_src_path, 'ref')
    docs_assets_path = os.path.join(docs_src_path, 'assets')
    docs_build_path = os.path.join(build_dir, 'docs')

    log.info('Ensuring assets directory <94>{}<32> exists', docs_assets_path)
    if not os.path.exists(docs_assets_path):
        os.makedirs(docs_assets_path)

    if recreate and os.path.exists(docs_out_path):
        log.info("<91>Deleting <94>{}".format(docs_out_path))
        shutil.rmtree(docs_out_path)

    if refdoc_paths:
        _gen_ref_docs(docs_ref_path, no_index)
    else:
        log.err('Not generating any reference documentation - '
                'No REFDOC_PATHS specified in config')

    with conf.within_proj_dir(docs_src_path):
        log.info('Building docs with <35>sphinx')
        shell.run('sphinx-build -b html -d {build} {docs} {out}'.format(
            build=docs_build_path,
            docs=docs_src_path,
            out=docs_out_path,
        ))
        ))


def _gen_ref_docs(ref_path, no_index=False):
    import os.path
    import shutil
    import sys
    from peltak.core import conf
    from peltak.core import log
    try:
        from refdoc import generate_docs as _generate_docs
    except ImportError:
        print("You need to install sphinx-refdoc to use the 'docs' command",
              file=sys.stderr)
        sys.exit(-1)

    refdoc_paths = conf.get('REFDOC_PATHS', [])

    log.info('Removing previously generated reference documentation')
    if os.path.exists(ref_path):
        shutil.rmtree(ref_path)

    os.makedirs(ref_path)

    log.info('Generating reference documentation')
    args = {'out_dir': ref_path}

    if no_index:
        args['no_index'] = True

    pkg_paths = [conf.proj_path(p) for p in refdoc_paths]

    _generate_docs(pkg_paths, **args)
