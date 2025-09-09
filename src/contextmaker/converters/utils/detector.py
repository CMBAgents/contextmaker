"""
Detection utilities for converters.
Handles format detection and library path finding.

IMPORTANT: Documentation type detection now allows coexistence of multiple types:
- Sphinx documentation (highest priority for conversion)
- Jupyter notebooks (can be added to any documentation type)
- Python docstrings (can coexist with notebooks)
- Raw source code (can coexist with notebooks and docstrings)

This enables comprehensive documentation extraction from libraries with mixed content.
"""

import os
import ast
import glob
import logging
import platform
import subprocess
import sys
import shutil

logger = logging.getLogger(__name__)


def find_sphinx_makefile(lib_path: str) -> str | None:
    """
    Recursively search for a Sphinx Makefile in the library directory.
    Prioritizes documentation directories (doc/, docs/) over root directory.
    
    Args:
        lib_path (str): Path to the root of the library.
        
    Returns:
        str | None: Path to the directory containing the Makefile, or None if not found.
    """
    # Check if 'make' command is available before searching for Makefiles
    if not shutil.which("make"):
        logger.debug("'make' command not available, skipping Makefile search")
        return None
    
    # First, check documentation directories specifically
    doc_dirs = ['doc', 'docs', 'documentation']
    for doc_dir in doc_dirs:
        doc_path = os.path.join(lib_path, doc_dir)
        if os.path.exists(doc_path):
            makefile_path = os.path.join(doc_path, 'Makefile')
            if os.path.exists(makefile_path):
                try:
                    with open(makefile_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Check if this Makefile contains Sphinx-related targets
                    if any(target in content.lower() for target in ['sphinx', 'html', 'docs', 'build']):
                        logger.info(f"Found Sphinx Makefile in documentation directory: {makefile_path}")
                        return doc_path
                except Exception as e:
                    logger.debug(f"Could not read Makefile {makefile_path}: {e}")
                    continue
    
    # If no documentation Makefile found, search recursively
    for root, dirs, files in os.walk(lib_path):
        # Skip common non-relevant directories for performance
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules', '.venv', 'venv']]
        
        for file in files:
            if file.lower() == 'makefile':
                makefile_path = os.path.join(root, file)
                try:
                    with open(makefile_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Check if this Makefile contains Sphinx-related targets
                    if any(target in content.lower() for target in ['sphinx', 'html', 'docs', 'build']):
                        logger.info(f"Found Sphinx Makefile at: {makefile_path}")
                        return root
                except Exception as e:
                    logger.debug(f"Could not read Makefile {makefile_path}: {e}")
                    continue
    return None


def has_sphinx_makefile(lib_path: str) -> bool:
    """
    Check if the library contains a Sphinx Makefile.
    
    Args:
        lib_path (str): Path to the library.
        
    Returns:
        bool: True if a Sphinx Makefile is found and 'make' is available, else False.
    """
    # First check if 'make' is available
    if not shutil.which("make"):
        return False
    
    return find_sphinx_makefile(lib_path) is not None


def get_best_sphinx_method(lib_path: str) -> tuple[str, str | None]:
    """
    Determine the best Sphinx documentation method to use based on system capabilities.
    
    Args:
        lib_path (str): Path to the library root
        
    Returns:
        tuple[str, str | None]: (method_type, method_specific_path)
            - method_type: 'sphinx_makefile', 'sphinx_direct', or 'sphinx_standard'
            - method_specific_path: Path to Makefile directory or Sphinx source, or None
    """
    # First check for Sphinx Makefile
    makefile_dir = find_sphinx_makefile(lib_path)
    
    if makefile_dir:
        if shutil.which("make"):
            logger.info("Sphinx Makefile found and 'make' is available - using highest priority method")
            return 'sphinx_makefile', makefile_dir
        else:
            logger.info("Sphinx Makefile found but 'make' not available - will use direct Sphinx building")
            return 'sphinx_direct', makefile_dir
    
    # Check for standard Sphinx documentation
    sphinx_source = find_sphinx_source(lib_path)
    if sphinx_source:
        logger.info("Standard Sphinx documentation found")
        return 'sphinx_standard', sphinx_source
    
    return 'none', None


def find_format(lib_path: str) -> str:
    """
    Detect the documentation format of a given library.
    Priority order:
    1. Sphinx Makefile (highest priority) - if 'make' is available
    2. Sphinx documentation (fallback if Makefile found but 'make' unavailable)
    3. Jupyter notebooks
    4. Inline docstrings
    5. Raw source code

    Args:
        lib_path (str): Path to the root of the library.

    Returns:
        str: One of ['sphinx_makefile', 'sphinx', 'notebook', 'docstrings', 'source'].

    Raises:
        ValueError: If no valid format is detected.
    """
    # Special handling for CAMB: always use sphinx_makefile to trigger special logic
    if _is_camb_library(lib_path):
        logger.info("CAMB detected: forcing sphinx_makefile format to use special logic")
        return 'sphinx_makefile'
    
    # First check for Sphinx Makefile
    makefile_dir = find_sphinx_makefile(lib_path)
    
    if makefile_dir:
        if shutil.which("make"):
            logger.info("Detected Sphinx Makefile - using highest priority method.")
            return 'sphinx_makefile'
        else:
            logger.info("Sphinx Makefile found but 'make' command not available.")
            logger.info("Install GNU Make to use the highest priority Makefile method.")
            logger.info("Falling back to standard Sphinx method.")
            # Continue to check for standard Sphinx documentation
    
    # Check for standard Sphinx documentation
    if has_documentation(lib_path):
        logger.info("Detected Sphinx-style documentation.")
        return 'sphinx'
    elif has_notebook(lib_path):
        logger.info("Detected Jupyter notebooks.")
        return 'notebook'
    elif has_docstrings(lib_path):
        logger.info("Detected inline docstrings.")
        return 'docstrings'
    elif has_source(lib_path):
        logger.info("Detected raw source code.")
        return 'source'
    else:
        # For installed packages without documentation, try to extract docstrings from source
        logger.info("Detected installed package, extracting docstrings from source code.")
        return 'docstrings'


def find_sphinx_source(lib_path: str) -> str | None:
    """
    Find the Sphinx documentation source directory.

    Args:
        lib_path (str): Path to the library.

    Returns:
        str: Path to the Sphinx source directory, or None if not found.
    """
    # Check for all possible Sphinx documentation locations
    possible_sources = [
        os.path.join(lib_path, "docs", "source"),  # docs/source
        os.path.join(lib_path, "docs"),            # docs
        os.path.join(lib_path, "doc", "source"),   # doc/source
        os.path.join(lib_path, "doc")              # doc
    ]
    
    for candidate in possible_sources:
        conf_py = os.path.join(candidate, "conf.py")
        index_rst = os.path.join(candidate, "index.rst")
        if os.path.exists(conf_py) and os.path.exists(index_rst):
            return candidate
    
    return None


def has_documentation(lib_path: str) -> bool:
    """
    Check if the library contains a Sphinx documentation folder.

    Args:
        lib_path (str): Path to the library.

    Returns:
        bool: True if Sphinx files exist, else False.
    """
    return find_sphinx_source(lib_path) is not None


def has_notebook(lib_path: str) -> bool:
    """
    Check if the library contains Jupyter notebooks.

    Args:
        lib_path (str): Path to the library.

    Returns:
        bool: True if at least one .ipynb file exists.
    """
    # Remove the restriction: notebooks can coexist with other documentation types

    for root, dirs, files in os.walk(lib_path):
        # Skip common non-relevant directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules']]
        
        for file in files:
            if file.endswith('.ipynb'):
                return True
    return False


def has_docstrings(lib_path: str) -> bool:
    """
    Check if the library contains Python files with docstrings.

    Args:
        lib_path (str): Path to the library.

    Returns:
        bool: True if at least one Python file with docstrings exists, else False.
    """
    # Only exclude if Sphinx documentation exists, allow notebooks and docstrings to coexist
    if has_documentation(lib_path):
        return False

    for root, dirs, files in os.walk(lib_path):
        # Skip common non-relevant directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if has_docstrings_in_file(file_path):
                    return True
    return False


def has_docstrings_in_file(file_path: str) -> bool:
    """
    Check if a specific Python file contains docstrings.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        bool: True if the file contains docstrings, else False.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Check module docstring
        if ast.get_docstring(tree):
            return True
        
        # Check class and function docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if ast.get_docstring(node):
                    return True
        
        return False
        
    except Exception:
        return False


def has_source(lib_path: str) -> bool:
    """
    Check if the library contains Python source files.

    Args:
        lib_path (str): Path to the library.

    Returns:
        bool: True if at least one .py file exists, else False.
    """
    # Only exclude if Sphinx documentation exists, allow notebooks, docstrings and source to coexist
    if has_documentation(lib_path):
        return False

    for root, dirs, files in os.walk(lib_path):
        # Skip common non-relevant directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                return True
    return False


def find_library_path(library_name: str) -> str | None:
    """
    Find the path to a library on the system.
    
    Args:
        library_name (str): Name of the library to find.
        
    Returns:
        str | None: Path to the library, or None if not found.
    """
    # ONLY check if the library is in the current working directory or subdirectories (repos clonés)
    current_dir = os.getcwd()
    repo_paths = [
        os.path.join(current_dir, library_name),
        os.path.join(current_dir, "..", library_name),
        os.path.join(current_dir, "..", "..", library_name),
        os.path.join(current_dir, "..", "..", "..", library_name),
        os.path.join(current_dir, "..", "..", "..", "..", library_name),
    ]
    
    for path in repo_paths:
        if os.path.exists(path) and os.path.isdir(path):
            logger.info(f"Found library '{library_name}' in repo at: {path}")
            return path
    
    logger.warning(f"Library '{library_name}' not found in repos. Make sure it's cloned in a parent directory.")
    return None


def get_default_output_path() -> str:
    """
    Get the default output path for converted documentation.
    
    Returns:
        str: Default output path.
    """
    home_dir = os.path.expanduser("~")
    default_path = os.path.join(home_dir, "contextmaker_output")
    return default_path


def ensure_camb_built(camb_dir: str):
    """
    Ensure the CAMB Fortran library is built. If not, build it automatically.
    Args:
        camb_dir (str): Path to the CAMB source directory (where setup.py is).
    Returns:
        bool: True if build successful or already built, False if build failed.
    """
    libname = "cambdll.dll" if platform.system() == "Windows" else "camblib.so"
    libpath = find_library_file(camb_dir, libname)
    if not libpath:
        setup_py = os.path.join(camb_dir, "setup.py")
        if not os.path.isfile(setup_py):
            logger.error(f"setup.py not found in {camb_dir}")
            return False
        logger.info(f"Building CAMB Fortran library in {camb_dir}...")
        result = subprocess.run([sys.executable, "setup.py", "make"], cwd=camb_dir)
        # Search again after build
        libpath = find_library_file(camb_dir, libname)
        if result.returncode != 0 or not libpath:
            logger.error("Failed to build CAMB Fortran library. Please check your Fortran compiler and dependencies.")
            return False
        logger.info(f"CAMB Fortran library built successfully at {libpath}.")
        return True
    else:
        logger.info(f"CAMB Fortran library already built at {libpath}.")
        return True


def find_library_file(camb_dir, libname):
    """
    Recursively search for the Fortran library file under camb_dir.
    Returns the first match or None if not found.
    """
    matches = glob.glob(os.path.join(camb_dir, '**', libname), recursive=True)
    return matches[0] if matches else None


def patch_camb_sys_exit(camb_dir: str):
    """
    Recursively replace sys.exit( with raise ImportError( in all .py files under camb_dir, except excluded files.
    Args:
        camb_dir (str): Path to the CAMB source directory.
    """
    ROOTS = [
        camb_dir,
        os.path.join(camb_dir, "camb"),
        os.path.join(camb_dir, "docs"),
        os.path.join(camb_dir, "fortran", "tests"),
    ]
    EXCLUDE = [
        os.path.normpath(os.path.join("fortran", "tests", "CAMB_test_files.py")),
    ]
    
    def patch_sys_exit_in_file(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if "sys.exit(" in content:
            logger.info(f"Patching sys.exit in {filepath}")
            content = content.replace("sys.exit(", "raise ImportError(")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    
    def should_patch(filepath):
        filepath_norm = os.path.normpath(filepath)
        for excl in EXCLUDE:
            if filepath_norm.endswith(excl):
                return False
        return True
    
    for root in ROOTS:
        if os.path.exists(root):
            for root_dir, dirs, files in os.walk(root):
                for file in files:
                    if file.endswith('.py') and should_patch(os.path.join(root_dir, file)):
                        patch_sys_exit_in_file(os.path.join(root_dir, file))


def aggregate_camb_text_files(camb_dir: str, output_file: str) -> bool:
    """
    Aggregate existing text files from CAMB docs/text directory in the order specified by index.rst.
    
    Args:
        camb_dir (str): Path to the CAMB source directory
        output_file (str): Path to the output markdown file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Paths for CAMB documentation
        docs_dir = os.path.join(camb_dir, "docs")
        source_dir = os.path.join(docs_dir, "source")
        text_dir = os.path.join(docs_dir, "text")
        index_rst = os.path.join(source_dir, "index.rst")
        
        # Check if text directory exists and has files
        if not os.path.exists(text_dir) or not os.listdir(text_dir):
            logger.warning("CAMB text directory not found or empty")
            return False
            
        # Read index.rst to get the order
        if not os.path.exists(index_rst):
            logger.warning("CAMB index.rst not found, will use alphabetical order")
            ordered_files = []
        else:
            ordered_files = _extract_camb_toctree_order(index_rst)
        
        # Get all text files
        text_files = []
        for root, dirs, files in os.walk(text_dir):
            for file in files:
                if file.endswith('.txt'):
                    text_files.append(os.path.join(root, file))
        
        if not text_files:
            logger.warning("No text files found in CAMB docs/text")
            return False
            
        logger.info(f"Found {len(text_files)} text files in CAMB docs/text")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write combined markdown file
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(f"# - camb | Complete Documentation -\n\n")
            out.write("## CAMB Documentation (from existing text files)\n\n")
            out.write(f"*Generated from: {docs_dir}*\n\n")
            
            # Add files in the specified order
            for i, doc_name in enumerate(ordered_files):
                # Find corresponding text file
                text_file = _find_camb_text_file(text_files, doc_name)
                if text_file:
                    if i > 0:
                        out.write("\n\n---\n\n")
                    
                    section_name = os.path.splitext(os.path.basename(text_file))[0]
                    out.write(f"## {section_name}\n\n")
                    
                    try:
                        with open(text_file, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            out.write(content)
                    except Exception as e:
                        out.write(f"*[Content could not be read: {e}]*\n")
                    
                    out.write("\n\n")
                    # Remove from text_files to avoid duplicates
                    text_files.remove(text_file)
            
            # Add any remaining text files in alphabetical order
            if text_files:
                out.write("\n\n---\n\n## Additional Documentation\n\n")
                for text_file in sorted(text_files):
                    section_name = os.path.splitext(os.path.basename(text_file))[0]
                    out.write(f"## {section_name}\n\n")
                    
                    try:
                        with open(text_file, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            out.write(content)
                    except Exception as e:
                        out.write(f"*[Content could not be read: {e}]*\n")
                    
                    out.write("\n\n")
        
        logger.info(f"CAMB text files aggregated successfully to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to aggregate CAMB text files: {e}")
        return False


def _extract_camb_toctree_order(index_rst_path: str) -> list:
    """Extract the order of files from CAMB index.rst toctree."""
    try:
        with open(index_rst_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all toctree sections
        toctree_sections = []
        current_section = []
        in_toctree = False
        
        for line in content.split("\n"):
            line = line.strip()
            if ".. toctree::" in line:
                in_toctree = True
                current_section = []
            elif in_toctree:
                if line and not line.startswith(":"):
                    # This is a document reference in the toctree
                    current_section.append(line)
                elif not line and current_section:
                    # Empty line after entries - end of this toctree
                    toctree_sections.append(current_section)
                    in_toctree = False
        
        # Add the last section if we're still in a toctree at the end
        if in_toctree and current_section:
            toctree_sections.append(current_section)
        
        # Flatten the list of sections
        ordered_files = []
        for section in toctree_sections:
            ordered_files.extend(section)
        
        return ordered_files
        
    except Exception as e:
        logger.warning(f"Could not extract toctree order from {index_rst_path}: {e}")
        return []


def _is_camb_library(lib_path: str) -> bool:
    """Check if the library is CAMB by looking for characteristic files/directories."""
    try:
        # Check for CAMB-specific files/directories (more specific indicators)
        camb_indicators = [
            os.path.join(lib_path, "camb"),
            os.path.join(lib_path, "docs", "markdown_builder.py"),
            os.path.join(lib_path, "camblib.so"),  # Fortran library
            os.path.join(lib_path, "cambdll.dll")  # Windows version
        ]
        
        for indicator in camb_indicators:
            if os.path.exists(indicator):
                return True
        
        # Check if the library name in the path contains 'camb'
        lib_name = os.path.basename(lib_path).lower()
        if 'camb' in lib_name:
            return True
            
        return False
        
    except Exception:
        return False


def _find_camb_text_file(text_files: list, doc_name: str) -> str | None:
    """Find the text file corresponding to a document name from index.rst."""
    # Remove .rst extension if present
    base_name = doc_name.replace('.rst', '')
    
    for text_file in text_files:
        file_base = os.path.splitext(os.path.basename(text_file))[0]
        if file_base == base_name:
            return text_file
    
    return None
