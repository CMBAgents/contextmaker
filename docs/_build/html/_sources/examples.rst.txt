Examples
========

This section provides practical examples of how to use ContextMaker for different scenarios.

Converting Sphinx Documentation
------------------------------

Example 1: Basic Sphinx Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a typical Sphinx project structure:

.. code-block:: bash

   myproject/
   ├── docs/
   │   ├── conf.py
   │   ├── index.rst
   │   └── api.rst
   └── src/
       └── myproject/

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path /path/to/myproject \
     --output_path ./converted_docs

Example 2: Sphinx with Custom Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path /path/to/myproject/docs \
     --output_path ./converted_docs \
     --library-name "MyScientificLibrary"

Converting Jupyter Notebooks
---------------------------

Example 3: Notebook Collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a collection of Jupyter notebooks:

.. code-block:: bash

   notebooks/
   ├── tutorial_01.ipynb
   ├── tutorial_02.ipynb
   └── examples.ipynb

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path ./notebooks \
     --output_path ./converted_docs

Converting Source Code
---------------------

Example 4: Python Package with Docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a Python package with comprehensive docstrings:

.. code-block:: bash

   mypackage/
   ├── mypackage/
   │   ├── __init__.py
   │   ├── core.py
   │   └── utils.py
   └── README.md

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path ./mypackage \
     --output_path ./converted_docs

Converting Mixed Content
-----------------------

Example 5: Project with Multiple Documentation Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a project with various documentation sources:

.. code-block:: bash

   scientific_project/
   ├── docs/
   │   ├── conf.py
   │   └── index.rst
   ├── notebooks/
   │   └── analysis.ipynb
   ├── src/
   │   └── scientific/
   └── README.md

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path ./scientific_project \
     --output_path ./converted_docs

Using the Markdown Builder Directly
---------------------------------

Example 6: Custom Sphinx to Markdown Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python converters/markdown_builder.py \
     --sphinx-source /path/to/project/docs \
     --output ./output.md \
     --source-root /path/to/project/src \
     --library-name "MyLibrary" \
     --exclude "internal,private"

Example 7: Including Notebooks in Sphinx Build
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python converters/markdown_builder.py \
     --sphinx-source /path/to/project/docs \
     --output ./output.md \
     --source-root /path/to/project/src \
     --notebook /path/to/project/notebooks/tutorial.ipynb

Python API Examples
------------------

Example 8: Programmatic Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import sys
   from contextmaker.contextmaker import main

   # Set up arguments programmatically
   sys.argv = [
       'contextmaker',
       '--input_path', '/path/to/myproject',
       '--output_path', './converted_docs',
       '--library-name', 'MyProject'
   ]

   # Run conversion
   main()

Example 9: Using Individual Converters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.converters.sphinx_converter import convert_sphinx_docs_to_txt
   from contextmaker.converters.nonsphinx_converter import create_final_markdown

   # Convert Sphinx docs
   success = convert_sphinx_docs_to_txt('/path/to/docs', './output')

   # Convert other formats
   create_final_markdown('/path/to/source', './output')

Example 10: Custom Markdown Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.converters.markdown_builder import build_markdown, combine_markdown

   # Build markdown from Sphinx
   build_dir = build_markdown('/path/to/docs', '/path/to/docs/conf.py', '/path/to/src')

   # Combine markdown files
   combine_markdown(build_dir, [], './output.md', '/path/to/docs/index.rst', 'MyLibrary') 