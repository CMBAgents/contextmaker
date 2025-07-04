API Reference
============

Main Module
----------

.. automodule:: contextmaker.contextmaker
   :members:
   :undoc-members:
   :show-inheritance:

Converters
----------

Auxiliary Functions
~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.auxiliary
   :members:
   :undoc-members:
   :show-inheritance:

Sphinx Converter
~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.sphinx_converter
   :members:
   :undoc-members:
   :show-inheritance:

Non-Sphinx Converter
~~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.nonsphinx_converter
   :members:
   :undoc-members:
   :show-inheritance:

Markdown Builder
~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.markdown_builder
   :members:
   :undoc-members:
   :show-inheritance:

Command Line Interface
---------------------

The main entry point for ContextMaker is the command line interface:

.. code-block:: bash

   python -m contextmaker.contextmaker [OPTIONS]

Arguments
---------

.. option:: --input_path, -i

   Path to the library documentation folder or project root.
   Required.

.. option:: --output_path, -o

   Path to the output folder for converted files.
   Required.

.. option:: --library-name

   Name of the library for the documentation title.
   Optional. Defaults to the basename of the input path.

.. option:: --exclude

   Comma-separated list of files to exclude (without extension).
   Optional.

Markdown Builder CLI
-------------------

The markdown builder tool has its own command line interface:

.. code-block:: bash

   python converters/markdown_builder.py [OPTIONS]

Arguments
---------

.. option:: --sphinx-source

   Path to Sphinx source directory (where conf.py and index.rst are).
   Required.

.. option:: --output

   Output file path for the generated markdown.
   Required.

.. option:: --source-root

   Absolute path to the root of the source code to add to sys.path for Sphinx autodoc.
   Required.

.. option:: --conf

   Path to conf.py (default: <sphinx-source>/conf.py).
   Optional.

.. option:: --index

   Path to index.rst (default: <sphinx-source>/index.rst).
   Optional.

.. option:: --notebook

   Path to notebook to convert and append.
   Optional.

.. option:: --library-name

   Name of the library for the documentation title.
   Optional.

.. option:: --exclude

   Comma-separated list of files to exclude (without .md extension).
   Optional.

Examples
--------

Basic Sphinx Conversion
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.contextmaker import main
   import sys

   # Convert Sphinx documentation
   sys.argv = [
       'contextmaker',
       '--input_path', '/path/to/myproject/docs',
       '--output_path', './converted_docs'
   ]
   main()

Source Code Conversion
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.converters.nonsphinx_converter import create_final_markdown

   # Convert source code with docstrings
   create_final_markdown('/path/to/source', './output')

Notebook Conversion
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.converters.markdown_builder import convert_notebook

   # Convert Jupyter notebook to markdown
   md_path = convert_notebook('/path/to/notebook.ipynb') 