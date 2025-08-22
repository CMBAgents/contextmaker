import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'ContextMaker'
copyright = '2025, Chadi Ait Ekioui'
author = 'Chadi Ait Ekioui'
release = '1.0.0'
version = '1.8.4'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

# To prevent Sphinx from failing on missing imports
autodoc_mock_imports = []

# Configuration for intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}

# Configuration for todos
todo_include_todos = True
