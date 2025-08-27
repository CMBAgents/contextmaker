Examples
========

This section provides practical examples of using ContextMaker for various scenarios.

Basic Examples
--------------

Convert NumPy Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Basic conversion to text
   contextmaker numpy

   # Convert to markdown
   contextmaker numpy --extension md

   # Custom output directory
   contextmaker numpy --output ./numpy_docs

   # Use specific numpy installation
   contextmaker numpy --input_path /usr/local/lib/python3.9/site-packages/numpy

Convert Scientific Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert pixell (CMB processing library)
   contextmaker pixell --output ./pixell_docs

   # Convert CAMB (cosmology library)
   contextmaker camb --output ./camb_docs

   # Convert scipy
   contextmaker scipy --extension md --output ./scipy_docs

Convert Custom Projects
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert project in current directory
   contextmaker myproject --input_path ./myproject

   # Convert with custom output
   contextmaker myproject --input_path ./myproject --output ./docs/myproject

   # Rough mode for direct file output
   contextmaker myproject --input_path ./myproject --output myproject.txt --rough

Advanced Examples
----------------

Batch Processing
~~~~~~~~~~~~~~~

Convert multiple libraries in sequence:

.. code-block:: bash

   # Simple loop
   for lib in numpy pandas matplotlib scipy; do
       echo "Converting $lib..."
       contextmaker $lib --output ./docs/$lib
   done

Using parallel processing:

.. code-block:: bash

   # Install parallel if not available
   # macOS: brew install parallel
   # Ubuntu: sudo apt-get install parallel

   # Convert libraries in parallel
   parallel contextmaker {} --output ./docs/{} ::: numpy pandas matplotlib scipy

   # With progress tracking
   parallel --bar contextmaker {} --output ./docs/{} ::: numpy pandas matplotlib scipy

Custom Library Paths
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert library from specific path
   contextmaker mylib --input_path /opt/mylib --output ./mylib_docs

   # Convert from git repository
   git clone https://github.com/user/mylib.git
   contextmaker mylib --input_path ./mylib --output ./mylib_docs

   # Convert from virtual environment
   contextmaker mylib --input_path ~/venv/lib/python3.9/site-packages/mylib

Programmatic Examples
--------------------

Basic Python Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.contextmaker import make

   # Simple conversion
   result = make("numpy")
   if result:
       print(f"Successfully converted numpy: {result}")

   # With custom parameters
   result = make(
       library_name="pixell",
       output_path="./pixell_docs",
       extension="md",
       rough=False
   )

   if result:
       print(f"✅ Pixell converted to: {result}")

Batch Processing in Python
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextmaker.contextmaker import make
   import concurrent.futures
   import os

   libraries = ["numpy", "pandas", "matplotlib", "scipy"]

   def convert_library(lib_name):
       """Convert a single library and return status."""
       try:
           result = make(
               library_name=lib_name,
               output_path=f"./docs/{lib_name}",
               extension="txt"
           )
           return lib_name, result, True, None
       except Exception as e:
           return lib_name, None, False, str(e)

   # Sequential processing
   print("Converting libraries sequentially...")
   for lib in libraries:
       lib_name, result, success, error = convert_library(lib)
       status = "✅" if success else "❌"
       print(f"{status} {lib_name}: {result or error}")

   # Parallel processing
   print("\nConverting libraries in parallel...")
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
       futures = [executor.submit(convert_library, lib) for lib in libraries]
       
       for future in concurrent.futures.as_completed(futures):
           lib_name, result, success, error = future.result()
           status = "✅" if success else "❌"
           print(f"{status} {lib_name}: {result or error}")

Error Handling and Logging
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from contextmaker.contextmaker import make

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )

   def safe_convert(library_name, **kwargs):
       """Safely convert library with comprehensive error handling."""
       try:
           logging.info(f"Starting conversion of {library_name}")
           
           result = make(library_name=library_name, **kwargs)
           
           if result:
               logging.info(f"✅ {library_name} converted successfully: {result}")
               return result
           else:
               logging.error(f"❌ {library_name} conversion failed")
               return None
               
       except ImportError as e:
           logging.error(f"❌ Import error for {library_name}: {e}")
           return None
       except PermissionError as e:
           logging.error(f"❌ Permission error for {library_name}: {e}")
           return None
       except Exception as e:
           logging.error(f"❌ Unexpected error for {library_name}: {e}")
           return None

   # Usage
   result = safe_convert("numpy", output_path="./numpy_docs")
   if result:
       print(f"Conversion completed: {result}")

Integration Examples
-------------------

GitHub Actions Workflow
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Convert Documentation
   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     convert-docs:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.9'
       
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install contextmaker
       
       - name: Convert documentation
         run: |
           contextmaker numpy --output ./docs/numpy
           contextmaker pandas --output ./docs/pandas
           contextmaker matplotlib --output ./docs/matplotlib
       
       - name: Upload artifacts
         uses: actions/upload-artifact@v3
         with:
           name: documentation
           path: ./docs/

Docker Integration
~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.9-slim

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       make \
       && rm -rf /var/lib/apt/lists/*

   # Install Python dependencies
   RUN pip install contextmaker

   # Set working directory
   WORKDIR /app

   # Copy script
   COPY convert_docs.py .

   # Run conversion
   CMD ["python", "convert_docs.py"]

And the corresponding Python script:

.. code-block:: python

   #!/usr/bin/env python3
   """Docker container script for converting documentation."""

   import os
   import sys
   from contextmaker.contextmaker import make

   def main():
       """Main conversion function."""
       libraries = os.environ.get('LIBRARIES', 'numpy,pandas').split(',')
       output_dir = os.environ.get('OUTPUT_DIR', '/app/docs')
       
       print(f"Converting libraries: {libraries}")
       print(f"Output directory: {output_dir}")
       
       for lib in libraries:
           lib = lib.strip()
           print(f"\nConverting {lib}...")
           
           try:
               result = make(
                   library_name=lib,
                   output_path=os.path.join(output_dir, lib),
                   extension="txt"
               )
               
               if result:
                   print(f"✅ {lib} converted successfully")
               else:
                   print(f"❌ {lib} conversion failed")
                   
           except Exception as e:
               print(f"❌ Error converting {lib}: {e}")
       
       print("\nConversion completed!")

   if __name__ == "__main__":
       main()

Real-World Scenarios
-------------------

Scientific Research Library
~~~~~~~~~~~~~~~~~~~~~~~~~~

Converting documentation for a scientific computing library:

.. code-block:: bash

   # Clone the library
   git clone https://github.com/scientific/mylib.git
   cd mylib

   # Convert documentation
   contextmaker mylib --input_path . --output ../mylib_docs --extension txt

   # Check the output
   ls -la ../mylib_docs/
   head -20 ../mylib_docs/mylib.txt

Legacy Documentation Modernization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Converting old documentation to modern formats:

.. code-block:: bash

   # Convert old Sphinx docs
   contextmaker legacy_lib --input_path /path/to/old/docs --output ./modern_docs

   # Convert to markdown for GitHub
   contextmaker legacy_lib --input_path /path/to/old/docs --output ./github_docs --extension md

API Documentation Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generating API docs from source code:

.. code-block:: bash

   # Convert library without documentation
   contextmaker mylib --input_path /path/to/source --output ./api_docs

   # This will extract docstrings and create API documentation

Performance Optimization
-----------------------

Large Library Processing
~~~~~~~~~~~~~~~~~~~~~~~

For very large libraries, use rough mode to save memory:

.. code-block:: bash

   # Process large library with rough mode
   contextmaker large_lib --output large_lib.txt --rough

   # Monitor memory usage
   contextmaker large_lib --output large_lib.txt --rough &
   top -p $!

Memory-Efficient Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import gc
   from contextmaker.contextmaker import make

   libraries = ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn"]

   for lib in libraries:
       print(f"Converting {lib}...")
       
       try:
           result = make(library_name=lib, output_path=f"./docs/{lib}")
           if result:
               print(f"✅ {lib} completed")
           else:
               print(f"❌ {lib} failed")
       except Exception as e:
           print(f"❌ {lib} error: {e}")
       
       # Force garbage collection between conversions
       gc.collect()
       print(f"Memory freed after {lib}")

Troubleshooting Examples
------------------------

Debug Conversion Issues
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Enable verbose logging
   contextmaker problem_lib --verbose

   # Check logs in real-time
   tail -f logs/conversion.log

   # Test with minimal parameters
   contextmaker problem_lib --output test.txt --rough

Handle Permission Issues
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check permissions
   ls -la /path/to/library
   ls -la /path/to/output

   # Fix permissions if needed
   chmod -R 755 /path/to/library
   chmod -R 755 /path/to/output

   # Use sudo if necessary (be careful!)
   sudo contextmaker library_name --output /path/to/output

Next Steps
----------

Now that you've seen practical examples:

- Try converting a library you use regularly
- Experiment with different output formats
- Set up batch processing for multiple libraries
- Integrate ContextMaker into your CI/CD pipeline
- Check the :doc:`api` for advanced programmatic usage
- Read :doc:`troubleshooting` for common issues and solutions 