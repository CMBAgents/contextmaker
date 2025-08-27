API Reference
=============

This section provides detailed API documentation for ContextMaker.

Core Module
-----------

contextmaker.contextmaker
~~~~~~~~~~~~~~~~~~~~~~~~~

Main entry point for the ContextMaker library.

.. automodule:: contextmaker.contextmaker
   :members:
   :undoc-members:
   :show-inheritance:

Main Function
~~~~~~~~~~~~

.. function:: make(library_name, output_path=None, extension='txt', input_path=None, rough=False)

   Convert library documentation to the specified format.

   **Parameters:**
   
   * **library_name** (str): Name of the library to convert
   * **output_path** (str, optional): Output directory or file path. Defaults to current directory
   * **extension** (str, optional): Output file extension ('txt' or 'md'). Defaults to 'txt'
   * **input_path** (str, optional): Manual path to library source. If None, auto-detection is used
   * **rough** (bool, optional): Output directly to file without creating folders. Defaults to False

   **Returns:**
   
   * **str or None**: Path to the converted file if successful, None otherwise

   **Raises:**
   
   * **ImportError**: If the library cannot be imported
   * **FileNotFoundError**: If the library source cannot be found
   * **PermissionError**: If there are permission issues
   * **Exception**: For other conversion errors

   **Example:**
   
   .. code-block:: python
   
      from contextmaker.contextmaker import make
      
      # Basic usage
      result = make("numpy")
      
      # With custom parameters
      result = make(
          library_name="pixell",
          output_path="./docs",
          extension="md",
          rough=False
      )

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~

.. function:: main()

   Main entry point for command line usage.

   **Usage:**
   
   .. code-block:: bash
   
      contextmaker library_name [options]
      
      Options:
        --output OUTPUT       Output directory or file path
        --extension {txt,md}  Output file extension (default: txt)
        --input_path INPUT_PATH
                              Manual path to library source
        --rough               Output directly to file without creating folders
        --verbose             Enable verbose logging
        --version             Show version information
        --help                Show help message

Converters
----------

Sphinx Makefile Converter
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.sphinx_makefile_converter
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: convert_sphinx_docs_to_txt(docs_path, output_path, source_root=None)

   Convert Sphinx documentation using Makefile.

   **Parameters:**
   
   * **docs_path** (str): Path to Sphinx documentation directory
   * **output_path** (str): Output path for converted documentation
   * **source_root** (str, optional): Path to source code root

   **Returns:**
   
   * **bool**: True if conversion successful, False otherwise

Sphinx Build Converter
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.sphinx_build_converter
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: convert_sphinx_docs_to_txt(docs_path, output_path, source_root=None)

   Convert Sphinx documentation using direct sphinx-build.

   **Parameters:**
   
   * **docs_path** (str): Path to Sphinx documentation directory
   * **output_path** (str): Output path for converted documentation
   * **source_root** (str, optional): Path to source code root

   **Returns:**
   
   * **bool**: True if conversion successful, False otherwise

Non-Sphinx Converter
~~~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.nonsphinx_converter
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: create_final_markdown(source_path, output_path, extension='txt')

   Convert non-Sphinx documentation to the specified format.

   **Parameters:**
   
   * **source_path** (str): Path to source code or documentation
   * **output_path** (str): Output path for converted documentation
   * **extension** (str): Output file extension ('txt' or 'md')

   **Returns:**
   
   * **bool**: True if conversion successful, False otherwise

Raw Source Code Converter
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.raw_source_code_converter
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: extract_documentation_from_source(source_path, output_path, extension='txt')

   Extract documentation from raw source code.

   **Parameters:**
   
   * **source_path** (str): Path to source code directory
   * **output_path** (str): Output path for extracted documentation
   * **extension** (str): Output file extension ('txt' or 'md')

   **Returns:**
   
   * **bool**: True if extraction successful, False otherwise

Notebook Converter
~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.notebook_converter
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: convert_notebooks_to_markdown(notebook_path, output_path, extension='txt')

   Convert Jupyter notebooks to the specified format.

   **Parameters:**
   
   * **notebook_path** (str): Path to notebook directory or file
   * **output_path** (str): Output path for converted documentation
   * **extension** (str): Output file extension ('txt' or 'md')

   **Returns:**
   
   * **bool**: True if conversion successful, False otherwise

Utility Modules
--------------

Detector
~~~~~~~~

.. automodule:: contextmaker.converters.utils.detector
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: detect_documentation_type(library_path)

   Detect the type of documentation in the library.

   **Parameters:**
   
   * **library_path** (str): Path to the library

   **Returns:**
   
   * **str**: Type of documentation ('sphinx', 'markdown', 'notebook', 'source', 'unknown')

.. function:: find_documentation_path(library_path)

   Find the path to documentation files.

   **Parameters:**
   
   * **library_path** (str): Path to the library

   **Returns:**
   
   * **str or None**: Path to documentation if found, None otherwise

Text Converter
~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.utils.text_converter
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: markdown_to_text(markdown_file, output_file)

   Convert Markdown file to plain text.

   **Parameters:**
   
   * **markdown_file** (str): Path to input Markdown file
   * **output_file** (str): Path to output text file

   **Returns:**
   
   * **bool**: True if conversion successful, False otherwise

.. function:: html_to_text(html_file, output_file)

   Convert HTML file to plain text.

   **Parameters:**
   
   * **html_file** (str): Path to input HTML file
   * **output_file** (str): Path to output text file

   **Returns:**
   
   * **bool**: True if conversion successful, False otherwise

Notebook Utils
~~~~~~~~~~~~~~

.. automodule:: contextmaker.converters.utils.notebook_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: find_notebooks(directory)

   Find all Jupyter notebooks in a directory.

   **Parameters:**
   
   * **directory** (str): Directory to search

   **Returns:**
   
   * **list**: List of notebook file paths

Dependency Installer
~~~~~~~~~~~~~~~~~~~

.. automodule:: contextmaker.utils.dependency_installer
   :members:
   :undoc-members:
   :show-inheritance:

.. function:: install_missing_dependencies()

   Install missing dependencies automatically.

   **Returns:**
   
   * **bool**: True if all dependencies are available, False otherwise

.. function:: check_dependency(dependency_name)

   Check if a specific dependency is available.

   **Parameters:**
   
   * **dependency_name** (str): Name of the dependency to check

   **Returns:**
   
   * **bool**: True if dependency is available, False otherwise

Configuration
------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

ContextMaker can be configured using environment variables:

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

Logging
-------

ContextMaker uses Python's built-in logging module with the following configuration:

.. code-block:: python

   import logging
   
   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('logs/conversion.log'),
           logging.StreamHandler()
       ]
   )

Log Levels
~~~~~~~~~~

- **DEBUG**: Detailed debugging information
- **INFO**: General information about conversion progress
- **WARNING**: Non-critical issues that don't stop conversion
- **ERROR**: Critical errors that prevent conversion

Custom Logging
~~~~~~~~~~~~~

You can customize logging behavior:

.. code-block:: python

   import logging
   from contextmaker.contextmaker import make
   
   # Set custom log level
   logging.getLogger('contextmaker').setLevel(logging.DEBUG)
   
   # Add custom handler
   handler = logging.FileHandler('custom.log')
   handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
   logging.getLogger('contextmaker').addHandler(handler)
   
   # Run conversion
   result = make("numpy")

Error Handling
-------------

Exception Types
~~~~~~~~~~~~~~

ContextMaker raises the following exceptions:

- **ImportError**: Library cannot be imported
- **FileNotFoundError**: Library source not found
- **PermissionError**: Permission issues
- **ValueError**: Invalid parameters
- **RuntimeError**: Conversion process errors

Error Handling Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.contextmaker import make
   
   try:
       result = make("problematic_lib")
       if result:
           print(f"Success: {result}")
       else:
           print("Conversion failed")
   except ImportError as e:
       print(f"Library not found: {e}")
   except PermissionError as e:
       print(f"Permission denied: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Custom Error Handling
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def safe_convert(library_name, **kwargs):
       """Safely convert library with custom error handling."""
       try:
           result = make(library_name=library_name, **kwargs)
           return result
       except ImportError:
           print(f"❌ Library '{library_name}' not found")
           return None
       except PermissionError:
           print(f"❌ Permission denied for '{library_name}'")
           return None
       except Exception as e:
           print(f"❌ Error converting '{library_name}': {e}")
           return None

Performance
-----------

Memory Management
~~~~~~~~~~~~~~~~

For large libraries, ContextMaker provides memory optimization:

.. code-block:: python

   # Use rough mode for large libraries
   result = make("large_lib", output_path="large_lib.txt", rough=True)
   
   # Force garbage collection between conversions
   import gc
   
   libraries = ["numpy", "pandas", "matplotlib"]
   for lib in libraries:
       result = make(lib)
       gc.collect()  # Free memory

Parallel Processing
~~~~~~~~~~~~~~~~~~

Process multiple libraries in parallel:

.. code-block:: python

   import concurrent.futures
   from contextmaker.contextmaker import make
   
   libraries = ["numpy", "pandas", "matplotlib"]
   
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
       futures = [executor.submit(make, lib) for lib in libraries]
       
       for future in concurrent.futures.as_completed(futures):
           result = future.result()
           print(f"Completed: {result}")

Caching
~~~~~~~

ContextMaker caches intermediate results to improve performance:

.. code-block:: python

   # First conversion (creates cache)
   result1 = make("numpy")
   
   # Second conversion (uses cache)
   result2 = make("numpy")
   
   # Clear cache if needed
   import shutil
   shutil.rmtree(".contextmaker_cache", ignore_errors=True)

Extending ContextMaker
---------------------

Custom Converters
~~~~~~~~~~~~~~~~~

You can create custom converters by extending the base classes:

.. code-block:: python

   from contextmaker.converters.base import BaseConverter
   
   class CustomConverter(BaseConverter):
       def convert(self, source_path, output_path, **kwargs):
           # Custom conversion logic
           pass
       
       def can_handle(self, source_path):
           # Check if this converter can handle the source
           return True

Custom Detectors
~~~~~~~~~~~~~~~

Create custom detection logic:

.. code-block:: python

   from contextmaker.converters.utils.detector import detect_documentation_type
   
   def custom_detector(library_path):
       # Custom detection logic
       if custom_condition:
           return "custom_type"
       return detect_documentation_type(library_path)

Plugin System
~~~~~~~~~~~~

ContextMaker supports a plugin system for extensions:

.. code-block:: python

   # Register custom converter
   from contextmaker.registry import register_converter
   
   register_converter("custom", CustomConverter)
   
   # Use custom converter
   result = make("library", converter_type="custom")

Next Steps
----------

Now that you understand the API:

- Check out :doc:`examples` for practical usage examples
- Read :doc:`usage` for command line usage
- Explore the source code for advanced customization
- Contribute to the project by extending functionality 