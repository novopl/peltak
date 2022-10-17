# -*- coding: utf-8 -*-
import os
import sys


project = u"peltak-pypi"
copyright = u"2021, Mateusz 'novo' Klos"
author = u"Mateusz 'novo' Klos"


def repo_path(path):
    ret = os.path.join(os.path.dirname(__file__), '../..', path)
    return os.path.normpath(ret)


sys.path.insert(0, repo_path('src'))
sys.path.insert(1, repo_path('.'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.imgmath',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    # 'sphinx.ext.viewcode',
    # 'sphinxcontrib.plantuml',
    'sphinx_autodoc_typehints',
]
# plantuml = 'java -jar {}'.format(repo_path('docs/bin/plantuml/plantuml.1.2019.9.jar'))
# plantuml_output_format = 'svg'

import peltak_pypi
version = peltak_pypi.__version__
release = peltak_pypi.__version__

doctest_test_doctest_blocks='default'
source_suffix = '.rst'
master_doc = 'index'
language = None

# templates_path = [repo_path('docs/_templates')]
exclude_patterns = [
    '_build',
    'env',
    'tmp',
    '.tox',
    'Thumbs.db',
    '.DS_Store'
]
todo_include_todos = False
intersphinx_mapping = {'https://docs.python.org/': None}

# = MAIN CONFIG ================================================================
default_role = 'any'
# pygments_style = 'monokai'
# html_static_path = [repo_path('docs/_static')]
# html_style='css/overrides.css'
html_theme = "sphinx_material"
html_theme_options = {
    # Set the name of the project to appear in the navigation.
    'nav_title': 'peltak-pypi',
    # Set you GA account ID to enable tracking
    'google_analytics_account': 'UA-187740680-1',
    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://novopl.github.io/peltak-pypi',
    # Set the color and the accent color
    'color_primary': 'light-green',
    'color_accent': 'amber',
    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/novopl/peltak-pypi',
    'repo_name': 'peltak-pypi',
    'logo_icon': '&#x267E',
    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 2,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': True,
}
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}


# = other ======================================================================
htmlhelp_basename = 'peltak-pypi'
latex_elements = {}
latex_documents = [
    (master_doc, 'peltak-pypi.tex', 'peltak-pypi Documentation',
     'Mateusz \'novo\' Klos', 'manual'),
]
man_pages = [
    (master_doc, 'peltak-pypi', 'peltak-pypi Documentation', [author], 1)
]
texinfo_documents = [
    (master_doc, 'peltak-pypi', 'peltak-pypi Documentation',
     author, 'peltak-pypi', 'One line description of project.',
     'Miscellaneous'),
]
