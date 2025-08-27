Installation
============

System Requirements
------------------

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows (with WSL recommended)
- **Memory**: At least 2GB RAM
- **Disk Space**: 500MB for installation, additional space for documentation

Prerequisites
-------------

GNU Make (for Sphinx Makefile support)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**macOS:**
.. code-block:: bash

   brew install make

**Ubuntu/Debian:**
.. code-block:: bash

   sudo apt-get update
   sudo apt-get install make

**CentOS/RHEL:**
.. code-block:: bash

   sudo yum install make

**Windows:**
Use WSL (Windows Subsystem for Linux) or install via Chocolatey:
.. code-block:: bash

   choco install make

Installation Methods
-------------------

Method 1: Development Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For developers and contributors:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/chadiaitekioui/contextmaker.git
   cd contextmaker

   # Create virtual environment
   python3 -m venv contextmaker_env
   source contextmaker_env/bin/activate  # On Windows: contextmaker_env\Scripts\activate

   # Install in development mode
   pip install -e .

Method 2: PyPI Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For end users:

.. code-block:: bash

   # Install from PyPI
   pip install contextmaker

Method 3: Conda Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install via conda
   conda install -c conda-forge contextmaker

Verification
-----------

After installation, verify that ContextMaker is working correctly:

.. code-block:: bash

   # Check version
   contextmaker --version

   # Check help
   contextmaker --help

   # Test with a simple library
   contextmaker --help

Dependencies
-----------

Core Dependencies
~~~~~~~~~~~~~~~~

The following packages are automatically installed:

- **sphinx** (>=5.0.0): Documentation building framework
- **jupytext** (>=1.14.0): Jupyter notebook handling
- **sphinx-rtd-theme** (>=1.0.0): ReadTheDocs theme
- **myst-parser** (>=1.0.0): Markdown parsing
- **sphinx-markdown-builder** (>=0.6.5): Markdown output
- **markdownify**: HTML to Markdown conversion
- **rich**: Rich text formatting
- **beautifulsoup4**: HTML parsing
- **html2text**: HTML to text conversion
- **markdown**: Markdown processing
- **numpy**: Numerical computing
- **docutils**: Document processing
- **jinja2**: Template engine
- **pygments**: Syntax highlighting
- **nbformat**: Notebook format handling
- **nbconvert**: Notebook conversion
- **jupyter**: Jupyter ecosystem

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~

For enhanced functionality:

.. code-block:: bash

   # Install development dependencies
   pip install -e ".[dev]"

   # Install additional tools
   pip install pandoc cmake

Configuration
------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

You can configure ContextMaker using environment variables:

.. code-block:: bash

   # Set default output directory
   export CONTEXTMAKER_OUTPUT_DIR="/path/to/output"

   # Set log level
   export CONTEXTMAKER_LOG_LEVEL="INFO"

   # Set default extension
   export CONTEXTMAKER_DEFAULT_EXTENSION="txt"

Configuration File
~~~~~~~~~~~~~~~~~

Create a configuration file at `~/.contextmaker/config.ini`:

.. code-block:: ini

   [defaults]
   output_dir = /path/to/output
   extension = txt
   log_level = INFO

   [logging]
   file_logging = true
   console_logging = true
   log_file = logs/conversion.log

Troubleshooting Installation
---------------------------

Common Issues
~~~~~~~~~~~~~

**1. "make command not found"**
.. code-block:: bash

   # Install GNU Make (see Prerequisites section)
   # Verify installation
   make --version

**2. Import Errors**
.. code-block:: bash

   # Reinstall in development mode
   pip install -e .

   # Check Python path
   python -c "import contextmaker; print(contextmaker.__file__)"

**3. Permission Errors**
.. code-block:: bash

   # Check file permissions
   ls -la /path/to/library

   # Use sudo if necessary (be careful!)
   sudo contextmaker library_name

**4. Virtual Environment Issues**
.. code-block:: bash

   # Deactivate and reactivate
   deactivate
   source contextmaker_env/bin/activate

   # Reinstall packages
   pip install -r requirements.txt

**5. Sphinx Build Errors**
.. code-block:: bash

   # Check Sphinx installation
   sphinx-build --version

   # Reinstall Sphinx
   pip install --upgrade sphinx

Getting Help
-----------

If you encounter installation issues:

1. **Check the logs**: Look at the error messages in the terminal
2. **Verify dependencies**: Ensure all prerequisites are installed
3. **Check Python version**: Ensure you're using Python 3.8+
4. **Search issues**: Check existing GitHub issues
5. **Create new issue**: Provide detailed error information

Next Steps
----------

Once ContextMaker is installed, you can:

- Read the :doc:`usage` guide to learn how to use it
- Check out :doc:`examples` for practical examples
- Explore the :doc:`api` for programmatic usage
- Learn about the :doc:`architecture` for advanced understanding
