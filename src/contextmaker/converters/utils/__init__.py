"""
Utilities package for converters.
Contains detection, markdown building, and text conversion utilities.
"""

from .detector import *
from .text_converter import *
from .notebook_utils import *

__all__ = [
    'find_format',
    'has_sphinx_makefile',
    'has_documentation',
    'has_notebook',
    'has_docstrings',
    'has_source',
    'find_library_path',
    'find_sphinx_source',
    'convert_markdown_to_txt',
    'markdown_to_text',
    'find_notebooks_in_doc_dirs',
    'find_all_notebooks_recursive',
    'convert_notebook',
    'append_notebook_markdown',
    'aggregate_camb_text_files',
    'markdown_builder',
    '_is_camb_library'
]
