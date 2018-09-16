# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import
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
            'build_dir': '.build',
            'docs': {
                'path': 'docs',
                'reference': [
                    'src/mypkg'
                ]
            }
        })

    Examples::

        \b
        $ peltak docs                           # Generate docs for the project
        $ peltak docs --no-index                # Skip main reference index
        $ peltak docs --recreate --no-index     # Build docs from clean slate

    """
    from .impl import docs

    docs.docs(recreate, gen_index)
