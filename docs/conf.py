import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'contextmaker'
copyright = '2025, Chadi Ait Ekioui'
author = 'Chadi Ait Ekioui'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # pour Google-style docstrings
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'  # beau thème ReadTheDocs

# Pour éviter que Sphinx n'échoue sur les imports manquants
autodoc_mock_imports = []
