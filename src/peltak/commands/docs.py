# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import, print_function
from . import cli, click


@cli.command('docs')
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
def docs(recreate, gen_index):
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
        conf.init({
            'BUILD_DIR': '.build',
            'DOC_SRC_PATH': 'docs',
            'REFDOC_PATHS': [
                'src/mypkg'
            ]
        })

    Examples::

        \b
        $ peltak docs                           # Generate docs for the project
        $ peltak docs --no-index                # Skip main reference index
        $ peltak docs --recreate --no-index     # Build docs from clean slate

    """
    import os.path
    import shutil
    from peltak.core import conf
    from peltak.core import log
    from peltak.core import shell

    build_dir = conf.get_path('BUILD_DIR', '.build')
    doc_src_path = conf.get_path('DOC_SRC_PATH', 'docs')
    refdoc_paths = conf.get('REFDOC_PATHS', [])

    docs_out_path = os.path.join(doc_src_path, 'html')
    docs_ref_path = os.path.join(doc_src_path, 'ref')
    docs_assets_path = os.path.join(doc_src_path, 'assets')
    docs_build_path = os.path.join(build_dir, 'docs')

    log.info('Ensuring assets directory <94>{}<32> exists', docs_assets_path)
    if not os.path.exists(docs_assets_path):
        os.makedirs(docs_assets_path)

    if recreate:
        for path in (docs_out_path, docs_build_path):
            if os.path.exists(path):
                log.info("<91>Deleting <94>{}".format(path))
                shutil.rmtree(path)

    if refdoc_paths:
        _gen_ref_docs(docs_ref_path, not gen_index)
    else:
        log.err('Not generating any reference documentation - '
                'No REFDOC_PATHS specified in config')

    with conf.within_proj_dir(doc_src_path):
        log.info('Building docs with <35>sphinx')
        shell.run('sphinx-build -b html -d {build} {docs} {out}'.format(
            build=docs_build_path,
            docs=doc_src_path,
            out=docs_out_path,
        ))
        log.info('You can view the docs by browsing to <34>file://{}'.format(
            os.path.join(docs_out_path, 'index.html')
        ))


def _gen_ref_docs(ref_path, no_index=False):
    import os.path
    import shutil
    import sys
    from peltak.core import conf
    from peltak.core import log
    try:
        from refdoc import generate_docs as _generate_docs
    except ImportError as ex:
        msg = ("You need to install sphinx-refdoc if you want to generate "
               "code reference docs.")

        print(msg, file=sys.stderr)
        log.err("Exception: {}".format(ex))
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
