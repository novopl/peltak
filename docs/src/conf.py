# -*- coding: utf-8 -*-
import os
import sys
import sphinx_rtd_theme


project = u"peltak"
copyright = u"2016-2018, Mateusz 'novo' Klos"
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
    'sphinx.ext.viewcode',
    'sphinxcontrib.plantuml',
]
plantuml = 'java -jar {}'.format(repo_path('docs/bin/plantuml/plantuml.1.2019.9.jar'))
plantuml_output_format = 'svg'

import peltak
version = peltak.__version__
release = peltak.__version__

doctest_test_doctest_blocks='default'
source_suffix = '.rst'
master_doc = 'index'
language = None

templates_path = [repo_path('docs/_templates')]
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

default_role = 'any'
pygments_style = 'monokai'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme = "sphinx_rtd_theme"
html_static_path = [repo_path('docs/_static')]
html_style='css/overrides.css'
htmlhelp_basename = 'peltak'

latex_elements = {}
latex_documents = [
    (master_doc, 'peltak.tex', 'peltak Documentation',
     'Mateusz \'novo\' Klos', 'manual'),
]
man_pages = [
    (master_doc, 'peltak', 'peltak Documentation', [author], 1)
]
texinfo_documents = [
    (master_doc, 'peltak', 'peltak Documentation',
     author, 'peltak', 'One line description of project.',
     'Miscellaneous'),
]
