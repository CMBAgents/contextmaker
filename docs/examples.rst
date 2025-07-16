Examples
========

This section provides practical examples of how to use ContextMaker for different scenarios.

Simple Usage Examples
--------------------

Example 1: Make pixell documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Clone pixell (if not already done)
   git clone https://github.com/simonsobs/pixell.git ~/Documents/GitHub/pixell

   # 2. Generate documentation
   contextmaker pixell

   # 3. Result: ~/your_context_library/pixell.txt

Example 2: Convert numpy documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Clone numpy
   git clone https://github.com/numpy/numpy.git ~/Documents/GitHub/numpy

   # 2. Generate documentation
   contextmaker numpy

   # 3. Result: ~/your_context_library/numpy.txt

Example 3: Custom output location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate documentation in custom location
   contextmaker pixell --output ~/Documents/my_documentation

   # Result: ~/Documents/my_documentation/pixell.txt

Converting Sphinx Documentation
------------------------------

Example 4: Manual path specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

   # Automatic search (if found in common locations)
   contextmaker myproject

   # Manual path specification
   contextmaker myproject --input_path /path/to/myproject

Example 5: Sphinx with custom configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   contextmaker myproject --input_path /path/to/myproject/docs --output ./custom_output

Converting Jupyter Notebooks
---------------------------

Example 6: Notebook collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a collection of Jupyter notebooks:

.. code-block:: bash

   notebooks/
   ├── tutorial_01.ipynb
   ├── tutorial_02.ipynb
   └── examples.ipynb

.. code-block:: bash

   contextmaker myproject --input_path ./notebooks

Converting Source Code
---------------------

Example 7: Python package with docstrings
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

   contextmaker mypackage --input_path ./mypackage

Converting Mixed Content
-----------------------

Example 8: Project with multiple documentation types
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

   contextmaker scientific_project --input_path ./scientific_project

Advanced Usage Examples
----------------------

Example 9: Direct module usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use the module directly
   python -m contextmaker.contextmaker pixell

Example 10: Manual Sphinx conversion with HTML->text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python src/contextmaker/converters/markdown_builder.py \
     --sphinx-source /path/to/project/docs \
     --output ./output.txt \
     --source-root /path/to/project/src \
     --html-to-text

Legacy Interface Examples
------------------------

Example 11: Legacy command line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path /path/to/myproject \
     --output_path ./converted_docs

Example 12: Legacy with library name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m contextmaker.contextmaker \
     --input_path /path/to/myproject/docs \
     --output_path ./converted_docs

Python API Examples
------------------

Example 13: Programmatic usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import sys
   from contextmaker.contextmaker import main

   # Set up arguments programmatically
   sys.argv = [
       'contextmaker',
       'pixell',
       '--output', './my_output'
   ]

   # Run conversion
   main()

Example 14: Using individual converters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.converters.sphinx_converter import convert_sphinx_docs_to_txt
   from contextmaker.converters.nonsphinx_converter import create_final_markdown

   # Convert Sphinx docs
   success = convert_sphinx_docs_to_txt('/path/to/docs', './output')

   # Convert other formats
   create_final_markdown('/path/to/source', './output')

Example 15: Custom markdown processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.converters.markdown_builder import build_html_and_convert_to_text

   # Build HTML and convert to text
   success = build_html_and_convert_to_text(
       '/path/to/docs', 
       '/path/to/docs/conf.py', 
       '/path/to/src', 
       './output.txt'
   ) 