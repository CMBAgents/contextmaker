Usage Guide
===========

Command Line Interface
---------------------

Basic Usage
~~~~~~~~~~~

The simplest way to use ContextMaker is to provide a library name:

.. code-block:: bash

   # Convert library documentation to text (default)
   contextmaker pixell

   # Convert to markdown format
   contextmaker pixell --extension md

   # Specify custom output path
   contextmaker pixell --output /path/to/output

   # Use manual library path
   contextmaker pixell --input_path /path/to/library

   # Rough mode (direct file output)
   contextmaker pixell --output output.txt --rough

Command Line Options
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   usage: contextmaker [-h] [--output OUTPUT] [--extension {txt,md}] 
                       [--input_path INPUT_PATH] [--rough] [--verbose] 
                       [--version] library_name

   positional arguments:
     library_name          Name of the library to convert

   optional arguments:
     -h, --help            show this help message and exit
     --output OUTPUT       Output directory or file path
     --extension {txt,md}  Output file extension (default: txt)
     --input_path INPUT_PATH
                           Manual path to library source
     --rough               Output directly to file without creating folders
     --verbose             Enable verbose logging
     --version             Show version information

Examples
--------

Convert NumPy Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Basic conversion to text
   contextmaker numpy

   # Convert to markdown with custom output
   contextmaker numpy --extension md --output ./numpy_docs

   # Use specific numpy installation
   contextmaker numpy --input_path /usr/local/lib/python3.9/site-packages/numpy

Convert Custom Library
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert library in current directory
   contextmaker mylib --input_path ./mylib

   # Convert with custom output
   contextmaker mylib --output ./docs/mylib --extension txt

Batch Processing
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert multiple libraries
   for lib in numpy pandas matplotlib; do
       contextmaker $lib --output ./docs/$lib
   done

   # Using parallel processing
   parallel contextmaker {} --output ./docs/{} ::: numpy pandas matplotlib

Programmatic Usage
-----------------

Basic Import
~~~~~~~~~~~

.. code-block:: python

   from contextmaker.contextmaker import make

   # Convert library documentation
   result = make(
       library_name="pixell",
       output_path="./output",
       extension="txt",
       rough=False
   )

   if result:
       print(f"Documentation converted successfully: {result}")

Advanced Usage
~~~~~~~~~~~~~

.. code-block:: python

   import os
   from contextmaker.contextmaker import make

   # Configuration
   config = {
       "library_name": "pixell",
       "output_path": "./docs",
       "extension": "md",
       "input_path": "/path/to/custom/pixell",
       "rough": False
   }

   # Convert with error handling
   try:
       result = make(**config)
       if result:
           print(f"✅ Success: {result}")
           # Get file size
           file_size = os.path.getsize(result)
           print(f"File size: {file_size / 1024 / 1024:.1f} MB")
       else:
           print("❌ Conversion failed")
   except Exception as e:
       print(f"Error: {e}")

Batch Processing
~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.contextmaker import make
   import concurrent.futures

   libraries = ["numpy", "pandas", "matplotlib", "scipy"]

   def convert_library(lib_name):
       try:
           result = make(
               library_name=lib_name,
               output_path=f"./docs/{lib_name}",
               extension="txt"
           )
           return lib_name, result, True
       except Exception as e:
           return lib_name, str(e), False

   # Parallel processing
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
       futures = [executor.submit(convert_library, lib) for lib in libraries]
       
       for future in concurrent.futures.as_completed(futures):
           lib_name, result, success = future.result()
           status = "✅" if success else "❌"
           print(f"{status} {lib_name}: {result}")

Output Formats
-------------

Text Format (.txt)
~~~~~~~~~~~~~~~~~~

The default output format is plain text, optimized for:

- **AI and ML processing**: Clean, structured text
- **Search indexing**: Easy to parse and index
- **Text analysis**: Natural language processing
- **Accessibility**: Screen reader friendly

Example output structure:

.. code-block:: text

   PIXELL LIBRARY DOCUMENTATION
   =============================

   OVERVIEW
   --------
   Pixell is a library for processing CMB maps and time-ordered data.

   INSTALLATION
   ------------
   pip install pixell

   API REFERENCE
   -------------
   pixell.reproject
   ---------------
   Reproject maps between different coordinate systems.

   Parameters:
   - map: Input map to reproject
   - shape: Output shape
   - wcs: World coordinate system

   Returns:
   - Reprojected map

   EXAMPLES
   --------
   import pixell
   # ... code examples ...

Markdown Format (.md)
~~~~~~~~~~~~~~~~~~~~

Markdown output preserves formatting and structure:

.. code-block:: markdown

   # PIXELL LIBRARY DOCUMENTATION

   ## Overview
   Pixell is a library for processing CMB maps and time-ordered data.

   ## Installation
   ```bash
   pip install pixell
   ```

   ## API Reference

   ### pixell.reproject
   Reproject maps between different coordinate systems.

   **Parameters:**
   - `map`: Input map to reproject
   - `shape`: Output shape
   - `wcs`: World coordinate system

   **Returns:**
   - Reprojected map

   ## Examples
   ```python
   import pixell
   # ... code examples ...
   ```

Conversion Methods
-----------------

ContextMaker automatically selects the best conversion method based on available documentation:

1. **Sphinx Makefile** (Priority 1)
   - Searches for `Makefile` with Sphinx targets
   - Executes `make html` command
   - Converts HTML output to text/markdown

2. **Sphinx Direct Build** (Priority 2)
   - Uses `sphinx-build` command directly
   - Processes `conf.py` and `.rst` files
   - Builds HTML documentation

3. **Non-Sphinx Documentation** (Priority 3)
   - Handles Markdown, docstrings, README files
   - Extracts documentation from source files
   - Processes various text formats

4. **Raw Source Code** (Priority 4)
   - Extracts code and docstrings directly
   - Creates documentation from source files
   - Fallback when no documentation found

5. **Jupyter Notebooks** (Priority 5)
   - Converts `.ipynb` files to documentation
   - Last resort fallback method

Logging and Monitoring
---------------------

Log Files
~~~~~~~~~

ContextMaker creates detailed logs in the `logs/` directory:

.. code-block:: text

   logs/
   ├── conversion.log      # Main conversion log
   ├── clean_logs.py       # Log cleaning utility
   └── logging_config.py   # Logging configuration

Log Format
~~~~~~~~~~

.. code-block:: text

   2025-08-28 00:15:01,807 [INFO] Starting conversion of library: pixell
   2025-08-28 00:15:01,808 [INFO] Detected Sphinx documentation
   2025-08-28 00:15:01,809 [INFO] Using Sphinx Makefile converter
   2025-08-28 00:15:02,100 [INFO] Sphinx build completed successfully
   2025-08-28 00:15:02,101 [INFO] Converting HTML to text
   2025-08-28 00:15:02,150 [INFO] ✅ Conversion successful! Mode: Sphinx Makefile, Output: pixell.txt, Size: 1.2 MB

Log Levels
~~~~~~~~~~

- **INFO**: General information about conversion progress
- **WARNING**: Non-critical issues that don't stop conversion
- **ERROR**: Critical errors that prevent conversion
- **DEBUG**: Detailed debugging information (with --verbose)

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**1. "Library not found"**
.. code-block:: bash

   # Check if library is installed
   python -c "import pixell; print(pixell.__file__)"

   # Use manual path
   contextmaker pixell --input_path /path/to/pixell

**2. "Permission denied"**
.. code-block:: bash

   # Check file permissions
   ls -la /path/to/library

   # Use sudo if necessary
   sudo contextmaker library_name

**3. "Conversion failed"**
.. code-block:: bash

   # Enable verbose logging
   contextmaker library_name --verbose

   # Check logs
   tail -f logs/conversion.log

**4. "Output directory not writable"**
.. code-block:: bash

   # Check output directory permissions
   ls -la /path/to/output

   # Create directory with proper permissions
   mkdir -p /path/to/output
   chmod 755 /path/to/output

Performance Optimization
----------------------

Memory Usage
~~~~~~~~~~~

- **Large libraries**: Use `--rough` mode for direct file output
- **Batch processing**: Process libraries sequentially to avoid memory issues
- **Output format**: Text format uses less memory than markdown

Speed Optimization
~~~~~~~~~~~~~~~~~

- **Parallel processing**: Use multiple processes for batch conversions
- **Caching**: ContextMaker caches intermediate results
- **Format selection**: Choose appropriate output format for your needs

Next Steps
----------

Now that you understand how to use ContextMaker:

- Check out :doc:`examples` for practical examples
- Explore the :doc:`api` for advanced programmatic usage
- Learn about the :doc:`architecture` for technical details
- Read :doc:`troubleshooting` for common issues and solutions 