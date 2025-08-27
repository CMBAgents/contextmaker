Introduction
============

What is ContextMaker?
---------------------

**ContextMaker** is an intelligent Python toolkit designed to automatically convert library documentation into formats optimized for AI agent ingestion, text analysis, and archival purposes. It features a sophisticated fallback system that ensures maximum compatibility across different documentation formats.

Key Features
-----------

🔍 **Intelligent Detection**
   Automatically detects documentation format (Sphinx, Markdown, docstrings, etc.)

🔄 **Smart Fallback System**
   Multiple conversion methods with automatic fallback for maximum compatibility

📚 **Multi-Format Support**
   Converts to both `.txt` and `.md` formats

🧹 **Automatic Dependency Management**
   Installs missing dependencies automatically

📝 **Comprehensive Logging**
   Detailed logs for debugging and monitoring

🎯 **Library Auto-Discovery**
   Finds libraries automatically on your system

Why ContextMaker?
-----------------

In today's data-driven world, having access to well-structured, machine-readable documentation is crucial for:

- **AI and Machine Learning**: Training models on documentation
- **Search and Indexing**: Creating searchable knowledge bases
- **Content Analysis**: Processing documentation for insights
- **Accessibility**: Making documentation available to screen readers
- **Archival**: Preserving documentation in standard formats

Traditional documentation often exists in various formats (HTML, PDF, notebooks, etc.) that are not easily processable by machines. ContextMaker solves this problem by providing a unified interface to convert any documentation into clean, structured text.

How It Works
------------

ContextMaker uses a **smart fallback system** with the following priority order:

1. **Sphinx Makefile** (Highest Priority)
   - Searches for `Makefile` with Sphinx targets
   - Uses `make html` command
   - Requires: GNU Make installed

2. **Sphinx Direct Build**
   - Uses `sphinx-build` command directly
   - Processes `conf.py` and `.rst` files
   - Requires: Sphinx installed

3. **Non-Sphinx Documentation**
   - Handles Markdown, docstrings, and other formats
   - Extracts documentation from source files
   - Requires: Basic Python packages

4. **Raw Source Code**
   - Extracts code and docstrings directly
   - Creates documentation from source files
   - Fallback: When no documentation found

5. **Jupyter Notebooks** (Last Resort)
   - Converts `.ipynb` files to documentation
   - Fallback: When all other methods fail

Architecture Overview
--------------------

.. code-block:: text

   contextmaker/
   ├── src/contextmaker/
   │   ├── contextmaker.py          # Main application logic
   │   ├── converters/              # Conversion engines
   │   │   ├── sphinx_makefile_converter.py    # Sphinx with Makefile
   │   │   ├── sphinx_build_converter.py       # Sphinx direct build
   │   │   ├── nonsphinx_converter.py          # Non-Sphinx documentation
   │   │   ├── raw_source_code_converter.py    # Raw source code extraction
   │   │   ├── notebook_converter.py           # Jupyter notebooks
   │   │   └── utils/                          # Converter utilities
   │   │       ├── detector.py                 # Format detection
   │   │       ├── notebook_utils.py          # Notebook handling
   │   │       └── text_converter.py          # Text conversion utilities
   │   └── utils/                             # Core utilities
   │       └── dependency_installer.py        # Dependency management
   ├── logs/                                 # Application logs
   ├── docs/                                # Documentation
   └── example/                             # Example files

Use Cases
---------

Documentation Conversion
~~~~~~~~~~~~~~~~~~~~~~~

- **Library Documentation**: Convert Sphinx docs to text
- **API References**: Extract function documentation
- **Tutorials**: Convert Jupyter notebooks to text
- **Source Code**: Generate docs from code comments

Content Processing
~~~~~~~~~~~~~~~~~

- **Text Analysis**: Process documentation for NLP
- **Search Indexing**: Create searchable text content
- **Archival**: Convert various formats to plain text
- **Accessibility**: Make docs accessible to screen readers

Next Steps
----------

Ready to get started? Check out the :doc:`installation` guide to set up ContextMaker on your system, or jump directly to :doc:`usage` to learn how to use it. 