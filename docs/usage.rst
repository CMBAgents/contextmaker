Usage Guide
==========

Installation
-----------

Clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/CMBAgents/Context_Maker
   cd Context_Maker
   python3 -m venv contextmaker_env
   source contextmaker_env/bin/activate
   pip install -e .

You can now open the source in your preferred IDE (VSCode, Emacs, etc.) for development.

Command Line Interface (CLI)
---------------------------

Once your virtual environment is activated and dependencies are installed, you can run **ContextMaker** from the command line.

Basic Usage
~~~~~~~~~~

.. code-block:: bash

   # Convert a library's documentation folder into a CMBAgent-friendly text file
   python -m contextmaker.contextmaker --input_path /path/to/library/docs --output_path ./converted_docs

   # Example: convert Sphinx docs
   python -m contextmaker.contextmaker --input_path ./my_library/docs --output_path ./my_library_converted

   # Convert a repository root folder (will auto-detect docs or source)
   python -m contextmaker.contextmaker --input_path ./my_library --output_path ./my_library_converted

Advanced Usage
~~~~~~~~~~~~~

.. code-block:: bash

   # Convert with specific library name
   python -m contextmaker.contextmaker --input_path /path/to/library --output_path ./output --library-name "MyLibrary"

   # Convert with excluded files
   python -m contextmaker.contextmaker --input_path /path/to/library --output_path ./output --exclude "internal,private"

Python API
---------

You can also use ContextMaker programmatically in your scripts:

.. code-block:: python

   from contextmaker.contextmaker import main
   import sys

   # Set up arguments
   sys.argv = [
       'contextmaker',
       '--input_path', '/path/to/library',
       '--output_path', './converted_docs'
   ]

   # Run conversion
   main()

Supported Input Formats
----------------------

Sphinx Documentation
~~~~~~~~~~~~~~~~~~~

* **Requirements**: conf.py + index.rst files
* **Location**: Typically in `docs/` or `docs/source/` directory
* **Features**: Full Sphinx support with autodoc, napoleon, and other extensions

.. code-block:: bash

   python -m contextmaker.contextmaker --input_path ./myproject/docs --output_path ./output

Markdown Files
~~~~~~~~~~~~~

* **Supported**: README.md, documentation.md, etc.
* **Features**: Preserves formatting and structure

.. code-block:: bash

   python -m contextmaker.contextmaker --input_path ./myproject --output_path ./output

Jupyter Notebooks
~~~~~~~~~~~~~~~~

* **Supported**: .ipynb files
* **Features**: Converts to markdown format using jupytext

.. code-block:: bash

   python -m contextmaker.contextmaker --input_path ./notebooks --output_path ./output

Python Source Code
~~~~~~~~~~~~~~~~~

* **Supported**: .py files with docstrings
* **Features**: Auto-generates API documentation from source code

.. code-block:: bash

   python -m contextmaker.contextmaker --input_path ./src --output_path ./output

Output Format
------------

ContextMaker produces a clean, standardized text file (`.txt`) containing:

* **Structured Content**: Organized sections with clear headers
* **Clean Formatting**: Removed HTML tags and unnecessary formatting
* **LLM Optimized**: Text format optimized for AI agent ingestion
* **Complete Documentation**: All relevant information from the source

Example Output Structure
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   # - MyLibrary | Complete Documentation -

   ## Introduction

   This is the main documentation for MyLibrary...

   ## API Reference

   ### Class MyClass

   This class provides...

   ### Function my_function

   This function does...

   ## Examples

   Here are some usage examples...

Markdown Builder Tool
--------------------

The script `converters/markdown_builder.py` allows you to generate Sphinx documentation of a Python library into a single Markdown file, usable as context for LLMs.

Usage
~~~~~

.. code-block:: bash

   python converters/markdown_builder.py \
     --sphinx-source /path/to/myproject/docs \
     --output /path/to/output.md \
     --source-root /path/to/myproject/myproject 