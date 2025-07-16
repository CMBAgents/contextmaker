Usage Guide
==========

Installation
-----------

Clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/chadiaitekioui/contextmaker
   cd contextmaker
   python3 -m venv contextmaker_env
   source contextmaker_env/bin/activate
   pip install -e .

You can now use ContextMaker from the command line.

Simple Command Line Interface
----------------------------

ContextMaker automatically finds libraries on your system and generates complete documentation with function signatures and docstrings.

Basic Usage
~~~~~~~~~~

.. code-block:: bash

   # Convert a library's documentation (automatic search)
   contextmaker library_name

   # Example: make pixell documentation
   contextmaker pixell

   # Example: convert numpy documentation
   contextmaker numpy

Advanced Usage
~~~~~~~~~~~~~

.. code-block:: bash

   # Specify custom output path
   contextmaker pixell --output ~/Documents/my_docs

   # Specify manual input path (overrides automatic search)
   contextmaker pixell --input_path /path/to/library/source

   # You can choose the output format using the --extension/-e flag (txt or md, default is txt)
   contextmaker pixell --extension md

Output
------

ContextMaker produces a clean, standardized text file (`.txt`) containing:

* **Default location**: `~/your_context_library/library_name.txt`
* **Content**: Complete documentation with function signatures, docstrings, examples, and API references
* **Format**: Clean text optimized for AI agent ingestion

Example Output Structure
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   # - Pixell | Complete Documentation -

   ## Introduction

   This is the main documentation for Pixell...

   ## Reference

   ### enmap - General map manipulation

   #### copy(_order ='C')

   This function creates a copy of the ndmap...

   #### sky2pix(_coords_ , _safe =True_, _corner =False_)

   Convert sky coordinates to pixel coordinates...

   ## Examples

   Here are some usage examples...

Supported Input Formats
----------------------

Sphinx Documentation
~~~~~~~~~~~~~~~~~~~

* **Requirements**: conf.py + index.rst files in `docs/` or `doc/` directory
* **Features**: Complete documentation with function signatures and docstrings
* **Workflow**: HTML generation → text conversion for maximum detail

.. code-block:: bash

   contextmaker pixell

Markdown Files
~~~~~~~~~~~~~

* **Supported**: README.md, documentation.md, etc.
* **Features**: Preserves formatting and structure

.. code-block:: bash

   contextmaker myproject --input_path /path/to/markdown/files

Jupyter Notebooks
~~~~~~~~~~~~~~~~

* **Supported**: .ipynb files
* **Features**: Converts to markdown format using jupytext

.. code-block:: bash

   contextmaker myproject --input_path /path/to/notebooks

Python Source Code
~~~~~~~~~~~~~~~~~

* **Supported**: .py files with docstrings
* **Features**: Auto-generates API documentation from source code

.. code-block:: bash

   contextmaker myproject --input_path /path/to/source

Library Requirements
-------------------

For complete documentation extraction, the library should have:

* A `docs/` or `doc/` directory containing `conf.py` and `index.rst`
* Source code accessible for docstring extraction

If only the installed package is found (without Sphinx docs), ContextMaker will extract available docstrings from the source code.

Advanced Usage for Developers
----------------------------

Direct Module Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use the module directly
   python -m contextmaker.contextmaker pixell

Manual Sphinx Conversion
~~~~~~~~~~~~~~~~~~~~~~~

For advanced users, you can use the markdown builder directly:

.. code-block:: bash

   python src/contextmaker/converters/markdown_builder.py \
     --sphinx-source /path/to/docs \
     --output /path/to/output.txt \
     --source-root /path/to/source \
     --html-to-text

Legacy Interface
~~~~~~~~~~~~~~~

The old interface is still available for backward compatibility:

.. code-block:: bash

   # Convert a library's documentation folder into a CMBAgent-friendly text file
   python -m contextmaker.contextmaker --input_path /path/to/library/docs --output_path ./converted_docs

   # Example: convert Sphinx docs
   python -m contextmaker.contextmaker --input_path ./my_library/docs --output_path ./my_library_converted

   # Convert a repository root folder (will auto-detect docs or source)
   python -m contextmaker.contextmaker --input_path ./my_library --output_path ./my_library_converted

Python API
---------

You can also use ContextMaker programmatically in your scripts:

.. code-block:: python

   from contextmaker.contextmaker import main
   import sys

   # Set up arguments
   sys.argv = [
       'contextmaker',
       'pixell',
       '--output', './my_output'
   ]

   # Run conversion
   main()

   # Or programmatically
   import contextmaker
   contextmaker.make("pixell", extension="md") 