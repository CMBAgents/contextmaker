#!/usr/bin/env python
"""
This script builds Sphinx documentation in Markdown format and combines it into a single file
for use as context with Large Language Models (LLMs).
"""

import argparse
import glob
import logging
import os
import shutil
import subprocess
import tempfile
import html2text
import re
import pkgutil

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def build_sphinx_directly(source_dir: str, output_format: str = 'text') -> str | None:
    """
    Build Sphinx documentation directly using Python without requiring 'make'.
    This is a fallback method when Makefile is not available.
    
    Args:
        source_dir (str): Path to the Sphinx source directory
        output_format (str): Desired output format ('text' or 'html')
        
    Returns:
        str | None: Path to the build directory if successful, None otherwise
    """
    logger.info(f"🔧 Building Sphinx documentation directly (Python fallback) from: {source_dir}")
    
    # Check if sphinx-build is available
    if not shutil.which("sphinx-build"):
        logger.error("❌ 'sphinx-build' command not found on this system.")
        logger.error("💡 Install Sphinx: pip install sphinx")
        return None
    
    try:
        # Determine build directory
        build_dir = os.path.join(source_dir, "_build")
        output_dir = os.path.join(build_dir, output_format)
        
        # Create build directory if it doesn't exist
        os.makedirs(build_dir, exist_ok=True)
        
        # Build command
        cmd = [
            "sphinx-build",
            "-b", output_format,
            "-d", os.path.join(build_dir, "doctrees"),
            source_dir,
            output_dir
        ]
        
        logger.info(f"🔧 Running: {' '.join(cmd)}")
        
        # Execute sphinx-build
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=source_dir
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Sphinx build successful! Output in: {output_dir}")
            return output_dir
        else:
            logger.error(f"❌ Sphinx build failed with return code: {result.returncode}")
            logger.error(f"❌ Error output: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error building Sphinx documentation: {e}")
        return None


def build_via_makefile(makefile_dir: str, source_root: str, output_format: str = 'text') -> str | None:
    """
    Build Sphinx documentation using the Makefile found in makefile_dir.
    
    Args:
        makefile_dir (str): Directory containing the Makefile
        source_root (str): Path to the source code root
        output_format (str): Desired output format ('text' or 'html')
        
    Returns:
        str | None: Path to the build directory if successful, None otherwise
    """
    # Check if 'make' command is available
    if not shutil.which("make"):
        logger.error("❌ 'make' command not found on this system.")
        logger.error("📋 Sphinx Makefile functionality requires GNU Make to be installed.")
        logger.error("💡 ContextMaker will automatically fall back to standard Sphinx method.")
        logger.error("🔧 To install GNU Make:")
        logger.error("   - macOS: Install Xcode Command Line Tools (xcode-select --install)")
        logger.error("   - Linux: sudo apt-get install make (Ubuntu/Debian) or sudo yum install make (RHEL/CentOS)")
        logger.error("   - Windows: Install MinGW, Cygwin, or use WSL")
        
        # Try to install make using the dependency manager
        try:
            from contextmaker.dependency_manager import dependency_manager
            if dependency_manager.install_system_package("make"):
                logger.info("✅ Successfully installed 'make', retrying build...")
                # Retry the build after installing make
                return build_via_makefile_internal(makefile_dir, source_root, output_format)
        except Exception as e:
            logger.error(f"❌ Failed to install 'make': {e}")
        
        return None
    
    return build_via_makefile_internal(makefile_dir, source_root, output_format)


def build_via_makefile_internal(makefile_dir: str, source_root: str, output_format: str = 'text') -> str | None:
    """
    Internal function to build Sphinx documentation using the Makefile.
    
    Args:
        makefile_dir (str): Directory containing the Makefile
        source_root (str): Path to the source code root
        output_format (str): Desired output format ('text' or 'html')
        
    Returns:
        str | None: Path to the build directory if successful, None otherwise
    """
    try:
        # Change to the makefile directory
        original_cwd = os.getcwd()
        os.chdir(makefile_dir)
        
        logger.info(f"📋 Building documentation via Makefile in: {makefile_dir}")
        
        # First, try to add a 'text' target to the Makefile if it doesn't exist
        makefile_path = os.path.join(makefile_dir, "Makefile")
        if os.path.exists(makefile_path):
            with open(makefile_path, 'r', encoding='utf-8') as f:
                makefile_content = f.read()
            
            # Check if 'text' target already exists
            if 'text:' not in makefile_content:
                logger.info("📋 Adding 'text' target to Makefile for text output")
                
                # Find the end of the Makefile and add the text target
                lines = makefile_content.split('\n')
                text_target_added = False
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('help:') or line.strip().startswith('.PHONY:'):
                        # Add text target before help or .PHONY
                        text_target = [
                            '',
                            '# Text output target added by contextmaker',
                            'text:',
                            '\t$(SPHINXBUILD) -b text $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/text"',
                            '\t@echo',
                            '\t@echo "Build finished. The text files are in $(BUILDDIR)/text."',
                            ''
                        ]
                        lines[i:i] = text_target
                        text_target_added = True
                        break
                
                if not text_target_added:
                    # Add at the end if no help or .PHONY found
                    text_target = [
                        '',
                        '# Text output target added by contextmaker',
                        'text:',
                        '\t$(SPHINXBUILD) -b text $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/text"',
                        '\t@echo',
                        '\t@echo "Build finished. The text files are in $(BUILDDIR)/text."',
                        ''
                    ]
                    lines.extend(text_target)
                
                # Write the modified Makefile
                with open(makefile_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                logger.info("✅ Added 'text' target to Makefile")
        
        # Try to build the documentation
        build_target = 'text' if output_format == 'text' else 'html'
        
        # First, try to clean any previous builds
        try:
            logger.info("🧹 Cleaning previous builds...")
            subprocess.run(["make", "clean"], capture_output=True, text=True, check=False)
        except Exception as e:
            logger.debug(f"Clean command failed (this is normal): {e}")
        
        # Build the documentation
        logger.info(f"🔨 Building documentation with target: {build_target}")
        result = subprocess.run(
            ["make", build_target],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
        )
        
        if result.returncode == 0:
            logger.info("✅ Makefile build successful")
            
            # Find the build directory
            build_dir = None
            if output_format == 'text':
                # Look for text output directory
                possible_text_dirs = [
                    os.path.join(makefile_dir, "_build", "text"),
                    os.path.join(makefile_dir, "build", "text"),
                    os.path.join(makefile_dir, "text")
                ]
                for dir_path in possible_text_dirs:
                    if os.path.exists(dir_path):
                        build_dir = dir_path
                        break
                
                # If still not found, check if _build directory exists and look for text subdirectory
                if not build_dir:
                    # Since we changed to makefile_dir, _build is now relative to current directory
                    build_base = "_build"
                    logger.debug(f"🔍 Checking build base: {build_base}")
                    if os.path.exists(build_base):
                        logger.debug(f"📁 Build base exists, checking contents...")
                        logger.debug(f"📁 Contents of build_base: {os.listdir(build_base)}")
                        for item in os.listdir(build_base):
                            item_path = os.path.join(build_base, item)
                            logger.debug(f"🔍 Checking item: {item_path}")
                            if os.path.isdir(item_path):
                                logger.debug(f"📁 Item is directory, checking for .txt files...")
                                try:
                                    txt_files = [f for f in os.listdir(item_path) if f.endswith('.txt') and os.path.isfile(os.path.join(item_path, f))]
                                    logger.debug(f"📝 Found .txt files: {txt_files}")
                                    if txt_files:
                                        build_dir = os.path.join(makefile_dir, item_path)
                                        logger.info(f"✅ Found build directory with .txt files: {build_dir}")
                                        break
                                except Exception as e:
                                    logger.debug(f"❌ Error checking item {item_path}: {e}")
                    else:
                        logger.debug(f"❌ Build base does not exist: {build_base}")
            else:
                # Look for HTML output directory
                possible_html_dirs = [
                    os.path.join(makefile_dir, "_build", "html"),
                    os.path.join(makefile_dir, "build", "html"),
                    os.path.join(makefile_dir, "html")
                ]
                for dir_path in possible_html_dirs:
                    if os.path.exists(dir_path):
                        build_dir = dir_path
                        break
            
            if build_dir:
                logger.info(f"📁 Build output found at: {build_dir}")
                return build_dir
            else:
                logger.warning("⚠️ Build succeeded but output directory not found")
                return None
        else:
            logger.error(f"❌ Makefile build failed with return code {result.returncode}")
            logger.error(f"stdout:\n{result.stdout}")
            logger.error(f"stderr:\n{result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error during Makefile build: {e}")
        return None
    finally:
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except Exception:
            pass


def create_safe_conf_py(original_conf_path):
    """
    Create a safe version of conf.py by removing problematic sys.exit() calls.
    Args:
        original_conf_path (str): Path to the original conf.py file
    Returns:
        str: Path to the temporary safe conf.py file, or None if failed
    """
    try:
        with open(original_conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file contains sys.exit() calls
        if 'sys.exit(' in content:
            logger.warning("Detected sys.exit() in conf.py, creating safe version.")
            
            # Create a temporary directory for the safe conf.py
            temp_dir = tempfile.mkdtemp(prefix="safe_conf_")
            safe_conf_path = os.path.join(temp_dir, "conf.py")
            
            # Remove or comment out sys.exit() calls
            # This regex matches sys.exit() calls and comments them out
            safe_content = re.sub(r'sys\.exit\([^)]*\)', '# sys.exit() - patched by contextmaker', content)
            
            with open(safe_conf_path, 'w', encoding='utf-8') as f:
                f.write(safe_content)
            
            logger.info(f" 📄 Created safe conf.py at: {safe_conf_path}")
            logger.info(f"Safe conf.py created: {safe_conf_path}")
            return safe_conf_path
        else:
            return original_conf_path
            
    except Exception as e:
        logger.error(f" 📄 Failed to create safe conf.py: {e}")
        logger.error(f"Failed to create safe conf.py: {e}")
        return original_conf_path


def create_minimal_conf_py(sphinx_source, source_root, notebooks_found=None):
    """
    Create a minimal working conf.py when the original one is problematic.
    Args:
        sphinx_source (str): Path to the Sphinx source directory
        source_root (str): Path to the source code root
        notebooks_found (list, optional): List of notebook paths found
    Returns:
        str: Path to the minimal conf.py file
    """
    # Detect all top-level modules in source_root
    autodoc_mock_imports = set()
    for importer, modname, ispkg in pkgutil.iter_modules([source_root]):
        autodoc_mock_imports.add(modname)
    # Also add submodules (one level deep)
    for importer, modname, ispkg in pkgutil.walk_packages([source_root]):
        autodoc_mock_imports.add(modname.split('.')[0])
    temp_dir = tempfile.mkdtemp(prefix="minimal_conf_")
    minimal_conf_path = os.path.join(temp_dir, "conf.py")
    # Add notebook support if notebooks were found
    notebook_extensions = []
    if notebooks_found:
        notebook_extensions = [
            'nbsphinx',  # For Jupyter notebook support
            'sphinx.ext.mathjax',  # For math in notebooks
        ]
        logger.info(f"📒 Adding notebook support extensions: {notebook_extensions}")
    
    minimal_conf_content = f'''# Minimal Sphinx configuration created by contextmaker
import os
import sys
sys.path.insert(0, r'{source_root}')
project = 'Library Documentation'
copyright = '2025'
author = 'ContextMaker'
release = '1.0.0'
version = '0.1.1'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    {', '.join(f"'{ext}'" for ext in notebook_extensions)}
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'alabaster'
autodoc_mock_imports = {sorted(list(autodoc_mock_imports))}
intersphinx_mapping = {{
    'python': ('https://docs.python.org/3/', None),
}}

# Notebook configuration
nbsphinx_execute = 'never'  # Don't execute notebooks during build
nbsphinx_allow_errors = True  # Continue build even if notebooks have errors
'''
    with open(minimal_conf_path, 'w', encoding='utf-8') as f:
        f.write(minimal_conf_content)
    logger.info(f"conf.py minimal : {minimal_conf_path}")
    logger.info(f"Minimal conf.py: {minimal_conf_path}")
    return minimal_conf_path


def parse_args():
    parser = argparse.ArgumentParser(description="Builds Sphinx documentation in Markdown for LLM.")
    parser.add_argument("--exclude", type=str, default="", help="List of files to exclude, separated by commas (without .md extension)")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file")
    parser.add_argument("--sphinx-source", type=str, required=True, help="Path to the Sphinx source folder (where conf.py and index.rst are located)")
    parser.add_argument("--conf", type=str, default=None, help="Path to conf.py (default: <sphinx-source>/conf.py)")
    parser.add_argument("--index", type=str, default=None, help="Path to index.rst (default: <sphinx-source>/index.rst)")
    parser.add_argument("--notebook", type=str, default=None, help="Path to a notebook to convert and add")
    parser.add_argument("--source-root", type=str, required=True, help="Absolute path to the source code root to add to sys.path for Sphinx autodoc.")
    parser.add_argument("--library-name", type=str, default=None, help="Library name for the documentation title.")
    parser.add_argument("--html-to-text", action="store_true", help="Builds the Sphinx doc in HTML then converts to text instead of Markdown.")
    return parser.parse_args()


def patch_sys_exit_in_py_files(root_dir):
    """
    Walk through all .py files under root_dir and comment out sys.exit() calls.
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if 'sys.exit(' in content:
                        patched = re.sub(r'sys\.exit\([^)]*\)', '# sys.exit() - patched by contextmaker', content)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(patched)
                        logger.info(f" 📄 Patched sys.exit() in {file_path}")
                        logger.info(f"Patched sys.exit() in {file_path}")
                except Exception as e:
                    logger.warning(f"Could not patch {file_path}: {e}")


def copy_and_patch_source(original_path):
    """
    Copy the original_path folder to a temporary folder and patch all .py files to neutralize sys.exit().
    Returns the path to the temporary folder.
    """
    temp_dir = tempfile.mkdtemp(prefix="patched_src_")
    dest_path = os.path.join(temp_dir, os.path.basename(original_path))
    if os.path.isdir(original_path):
        shutil.copytree(original_path, dest_path, dirs_exist_ok=True)
    else:
        shutil.copy2(original_path, dest_path)
    patch_sys_exit_in_py_files(dest_path)
    return dest_path


def build_markdown(sphinx_source, conf_path, source_root, robust=False):
    # Copy and patch source_root and sphinx_source folders
    patched_source_root = copy_and_patch_source(source_root)
    patched_sphinx_source = copy_and_patch_source(sphinx_source)
    # Use the conf.py from the patched folder
    patched_conf_path = os.path.join(patched_sphinx_source, os.path.basename(conf_path))
    build_dir = tempfile.mkdtemp(prefix="sphinx_build_")
    logger.info(f"Build directory: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)
    
    # Find notebooks early to include them in minimal config if needed
    notebooks_found = find_notebooks_in_doc_dirs(source_root)
    if notebooks_found:
        logger.info(f"📒 Found {len(notebooks_found)} notebooks that will be included in documentation")
    if robust:
        # Always use minimal conf.py
        minimal_conf_path = create_minimal_conf_py(patched_sphinx_source, patched_source_root, notebooks_found)
        conf_dir = os.path.dirname(minimal_conf_path)
        logger.info(f" 📄 Forcing minimal conf.py for robust mode: {minimal_conf_path}")
        logger.info(f"Using minimal conf.py for robust mode: {minimal_conf_path}")
        result = subprocess.run(
            ["sphinx-build", "-b", "markdown", "-c", conf_dir, patched_sphinx_source, build_dir],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": patched_source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
        )
        if result.returncode != 0:
            logger.error(" 📄 sphinx-build failed even with minimal configuration in robust mode.")
            logger.error("sphinx-build failed with minimal config (robust mode).")
            logger.error(" 📄 stdout:\n%s", result.stdout)
            logger.error(" 📄 stderr:\n%s", result.stderr)
    else:
        # Create a safe version of conf.py if needed
        safe_conf_path = create_safe_conf_py(patched_conf_path)
        conf_dir = os.path.dirname(safe_conf_path)
        logger.info(f"sphinx_source : {patched_sphinx_source}")
        logger.info(f"conf_path : {safe_conf_path}")
        logger.info(f"build_dir : {build_dir}")
        logger.info(f"Commande sphinx-build : sphinx-build -b markdown -c {conf_dir} {patched_sphinx_source} {build_dir}")
        logger.info("Lancement de sphinx-build...")
        logger.info(f"sphinx_source: {patched_sphinx_source}")
        logger.info(f"conf_path: {safe_conf_path}")
        logger.info(f"build_dir: {build_dir}")
        logger.info("Running sphinx-build for markdown output.")
        result = subprocess.run(
            ["sphinx-build", "-b", "markdown", "-c", conf_dir, patched_sphinx_source, build_dir],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": patched_source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
        )
        if result.returncode != 0:
            logger.error(f"sphinx-build failed with return code {result.returncode}")
            logger.error(" 📄 stdout:\n%s", result.stdout)
            logger.error(" 📄 stderr:\n%s", result.stderr)
            # Try with minimal conf.py
            minimal_conf_path = create_minimal_conf_py(patched_sphinx_source, patched_source_root, notebooks_found)
            conf_dir = os.path.dirname(minimal_conf_path)
            result = subprocess.run(
                ["sphinx-build", "-b", "markdown", "-c", conf_dir, patched_sphinx_source, build_dir],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": patched_source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
            )
            if result.returncode == 0:
                logger.info("sphinx-build succeeded with minimal config.")
                
                # Check if any markdown files were produced
                import glob
                md_files = glob.glob(os.path.join(build_dir, "*.md"))
                if md_files:
                    logger.info(f"✅ Minimal config produced {len(md_files)} markdown files")
                else:
                    logger.warning("⚠️ Minimal config succeeded but produced no markdown files")
                
                try:
                    temp_dir = os.path.dirname(minimal_conf_path)
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f" 📄 Failed to clean up minimal conf.py: {e}")
            else:
                logger.error(" 📄 sphinx-build failed even with minimal configuration.")
                logger.error(" 📄 stdout:\n%s", result.stdout)
                logger.error(" 📄 stderr:\n%s", result.stderr)
                try:
                    temp_dir = os.path.dirname(minimal_conf_path)
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f" 📄 Failed to clean up minimal conf.py: {e}")
    # Nettoyage des dossiers temporaires
    for temp in [patched_source_root, patched_sphinx_source]:
        try:
            shutil.rmtree(temp)
        except Exception:
            pass
    return build_dir


def extract_toctree_order_recursive(rst_path, seen=None):
    """
    Recursively extract the order of documents from .. toctree:: directives in rst files.
    Args:
        rst_path (str): Path to the rst file to parse.
        seen (set): Set of already seen rst file basenames (without extension) to avoid cycles.
    Returns:
        list: Ordered list of rst file basenames (without extension).
    """
    if seen is None:
        seen = set()
    try:
        with open(rst_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f" 📄  Could not read {rst_path}: {e}")
        return []

    toctree_docs = []
    in_toctree = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(".. toctree::"):
            in_toctree = True
            continue
        if in_toctree:
            if stripped == "" or stripped.startswith(":"):
                continue
            if stripped.startswith(".. "):  # another directive
                break
            doc = stripped
            if doc not in seen:
                seen.add(doc)
                toctree_docs.append(doc)
    # Recursively process referenced rst files
    result = []
    rst_dir = os.path.dirname(rst_path)
    for doc in toctree_docs:
        result.append(doc)
        doc_path = os.path.join(rst_dir, doc + ".rst")
        if os.path.exists(doc_path):
            subdocs = extract_toctree_order_recursive(doc_path, seen)
            for subdoc in subdocs:
                if subdoc not in result:
                    result.append(subdoc)
    return result


def combine_markdown(build_dir, exclude, output, index_path, library_name):
    md_files = glob.glob(os.path.join(build_dir, "*.md"))
    logger.info(f"Markdown files found: {[os.path.basename(f) for f in md_files]}")
    exclude_set = set(f"{e.strip()}.md" for e in exclude if e.strip())

    filtered = [f for f in md_files if os.path.basename(f) not in exclude_set]

    index_md = None
    others = []
    for f in filtered:
        if os.path.basename(f).lower() == "index.md":
            index_md = f
        else:
            others.append(f)

    # Use recursive toctree extraction
    toctree_order = extract_toctree_order_recursive(index_path) if index_path else []
    logger.info(f"Toctree order: {toctree_order}")
    name_to_file = {os.path.splitext(os.path.basename(f))[0]: f for f in others}
    ordered = []
    for doc in toctree_order:
        if doc in name_to_file:
            ordered.append(name_to_file.pop(doc))
        else:
            logger.warning(f"Referenced in toctree but .md not found: {doc}.md")

    remaining = sorted(name_to_file.values())
    if remaining:
        logger.info(f".md files not referenced in toctree: {[os.path.basename(f) for f in remaining]}")
    ordered.extend(remaining)

    final_order = ([index_md] if index_md else []) + ordered

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as out:
        out.write(f"# - {library_name} | Complete Documentation -\n\n")
        for i, f in enumerate(final_order):
            if i > 0:
                out.write("\n\n---\n\n")
            section = os.path.splitext(os.path.basename(f))[0]
            out.write(f"## {section}\n\n")
            with open(f, encoding="utf-8") as infile:
                out.write(infile.read())
                out.write("\n\n")

    logger.info(f"Combined markdown written to {output}")


def find_all_notebooks_recursive(library_root, exclude_patterns=None):
    """
    Find ALL .ipynb files recursively in the entire library, with intelligent exclusions.
    
    Args:
        library_root (str): Path to the library root
        exclude_patterns (list, optional): Additional patterns to exclude (e.g., ['*test*', '*temp*'])
    
    Returns:
        list: List of absolute paths to all notebooks found, sorted alphabetically
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    # Standard exclusions for performance and relevance
    standard_exclusions = {
        '.git', '__pycache__', 'build', 'dist', '.pytest_cache', 
        'node_modules', '.ipynb_checkpoints', '.jupyter', '.cache',
        'venv', 'env', '.venv', '.env', 'conda-meta',
        '_build', '.sphinx', '.tox', '.coverage', 'htmlcov'
    }
    
    # Add user exclusions
    all_exclusions = standard_exclusions.union(set(exclude_patterns))
    
    candidates = []
    total_dirs_scanned = 0
    total_files_scanned = 0
    
    logger.info(f"🔍 Starting recursive notebook search in: {library_root}")
    logger.info(f"🚫 Excluding patterns: {sorted(all_exclusions)}")
    
    for root, dirs, files in os.walk(library_root):
        total_dirs_scanned += 1
        
        # Filter out excluded directories (modify dirs in-place for os.walk)
        dirs[:] = [d for d in dirs if d not in all_exclusions]
        
        # Check for notebooks in current directory
        for file in files:
            total_files_scanned += 1
            if file.endswith('.ipynb'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, library_root)
                candidates.append((full_path, relative_path))
                logger.debug(f"📒 Found notebook: {relative_path}")
    
    # Sort by relative path for consistent ordering
    candidates.sort(key=lambda x: x[1])
    
    # Convert to absolute paths
    abs_candidates = [os.path.abspath(path) for path, _ in candidates]
    
    # Log summary
    logger.info(f"🔍 Search completed:")
    logger.info(f"   📁 Directories scanned: {total_dirs_scanned}")
    logger.info(f"   📄 Files scanned: {total_files_scanned}")
    logger.info(f"   📒 Notebooks found: {len(abs_candidates)}")
    
    if abs_candidates:
        logger.info(f"📒 All notebooks found:")
        for i, (_, rel_path) in enumerate(candidates, 1):
            logger.info(f"   {i:2d}. {rel_path}")
    else:
        logger.info(f"❌ No notebooks found in {library_root}")
    
    return abs_candidates


def find_notebooks_in_doc_dirs(library_root, recursive=True):
    """
    Find notebooks in documentation directories with option for recursive search.
    
    Args:
        library_root (str): Path to the library root
        recursive (bool): If True, search recursively in all subdirectories
    
    Returns:
        list: List of absolute paths to notebooks found
    """
    if recursive:
        logger.info(f"🔍 Using recursive search for notebooks in {library_root}")
        return find_all_notebooks_recursive(library_root)
    
    # Original behavior for backward compatibility
    logger.info(f"🔍 Using legacy search in docs/, doc/, docs/source/ for {library_root}")
    candidates = []
    for doc_dir in ["docs", "doc", "docs/source"]:
        abs_doc_dir = os.path.join(library_root, doc_dir)
        if os.path.isdir(abs_doc_dir):
            found = glob.glob(os.path.join(abs_doc_dir, "*.ipynb"))
            logger.info(f"Notebooks in {doc_dir}: {found}")
            candidates.extend(found)
    
    abs_candidates = sorted([os.path.abspath(nb) for nb in candidates])
    if abs_candidates:
        logger.info(f"Notebooks found: {abs_candidates}")
    else:
        logger.info(f"No notebooks found in docs/, doc/, or docs/source/ under {library_root}.")
    return abs_candidates


def convert_notebook(nb_path):
    logger.info(f"Converting notebook: {nb_path}")
    if not shutil.which("jupytext"):
        logger.error(" 📄 jupytext is required to convert notebooks.")
        return None
    md_path = os.path.splitext(nb_path)[0] + ".md"
    cmd = ["jupytext", "--to", "md", "--opt", "notebook_metadata_filter=-all", nb_path]
    logger.info("Running jupytext conversion...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f" 📄 Failed to convert notebook:\n{result.stderr}")
        return None
    if not os.path.exists(md_path):
        logger.error(f" 📄 Expected markdown file {md_path} not found after conversion.")
        return None
    logger.info(f"Notebook converted to {md_path}")
    return md_path


def append_notebook_markdown(output_file, notebook_md):
    logger.info(f"Appending notebook {notebook_md} to {output_file}")
    with open(output_file, "a", encoding="utf-8") as out, open(notebook_md, encoding="utf-8") as nb_md:
        out.write("\n\n# Notebook\n\n---\n\n")
        out.write(nb_md.read())
    logger.info(f"Notebook appended: {notebook_md}")


def build_html_and_convert_to_text(sphinx_source, conf_path, source_root, output):
    # Copie et patch du dossier source_root et sphinx_source
    patched_source_root = copy_and_patch_source(source_root)
    patched_sphinx_source = copy_and_patch_source(sphinx_source)
    # Use the conf.py from the patched folder
    patched_conf_path = os.path.join(patched_sphinx_source, os.path.basename(conf_path))
    build_dir = tempfile.mkdtemp(prefix="sphinx_html_build_")
    logger.info(f" 📄 Temporary HTML build directory: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)
    # Create a safe version of conf.py if needed
    safe_conf_path = create_safe_conf_py(patched_conf_path)
    conf_dir = os.path.dirname(safe_conf_path)
    logger.info(f" 📄 sphinx_source: {patched_sphinx_source}")
    logger.info(f" 📄 conf_path: {safe_conf_path}")
    logger.info(f" 📄 build_dir: {build_dir}")
    logger.info(f" 📄 sphinx-build command: sphinx-build -b html -c {conf_dir} {patched_sphinx_source} {build_dir}")
    logger.info(" 📄 Running sphinx-build (HTML)...")
    result = subprocess.run(
        ["sphinx-build", "-b", "html", "-c", conf_dir, patched_sphinx_source, build_dir],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": patched_source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
    )
    if result.returncode != 0:
        logger.error(f"sphinx-build failed with return code {result.returncode}")
        logger.error(" 📄 stdout:\n%s", result.stdout)
        logger.error(" 📄 stderr:\n%s", result.stderr)
        
        # Check for common error patterns and provide helpful messages
        stderr_lower = result.stderr.lower()
        if "sys.exit()" in result.stderr:
            logger.error(" 📄 The library's conf.py file contains sys.exit() calls, which prevents Sphinx from building.")
            logger.error(" 📄 This is a common issue with some libraries. The library may need to be properly installed or have its dependencies resolved.")
            logger.error(" 📄 Try installing the library and its dependencies first, or use a different documentation source.")
        elif "circular import" in stderr_lower or "partially initialized module" in stderr_lower:
            logger.error(" 📄 This appears to be a circular import issue. This is common with complex libraries like numpy.")
            logger.error(" 📄 The library may need to be properly installed or the documentation may have dependency issues.")
        elif "import error" in stderr_lower:
            logger.error(" 📄 Import error detected. The library may have missing dependencies for documentation building.")
        elif "configuration error" in stderr_lower:
            logger.error(" 📄 Configuration error detected. The library's Sphinx configuration may be incompatible.")
            logger.error(" 📄 This could be due to missing dependencies, incompatible extensions, or configuration issues.")
            logger.error(" 📄 Trying with minimal configuration...")
            
            # Try with minimal conf.py
            # Find notebooks for minimal config
            notebooks_in_source = find_notebooks_in_doc_dirs(source_root)
            minimal_conf_path = create_minimal_conf_py(patched_sphinx_source, patched_source_root, notebooks_in_source)
            conf_dir = os.path.dirname(minimal_conf_path)
            
            result = subprocess.run(
                ["sphinx-build", "-b", "html", "-c", conf_dir, patched_sphinx_source, build_dir],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": patched_source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
            )
            
            if result.returncode == 0:
                logger.info(" ✅ sphinx-build completed successfully with minimal configuration.")
                # Clean up minimal conf.py
                try:
                    temp_dir = os.path.dirname(minimal_conf_path)
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f" 📄 Failed to clean up minimal conf.py: {e}")
            else:
                logger.error(" 📄 sphinx-build failed even with minimal configuration.")
                logger.error(" 📄 stdout:\n%s", result.stdout)
                logger.error(" 📄 stderr:\n%s", result.stderr)
                # Clean up minimal conf.py
                try:
                    temp_dir = os.path.dirname(minimal_conf_path)
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f" 📄 Failed to clean up minimal conf.py: {e}")
                return False
    else:
        logger.info(" ✅ sphinx-build (HTML) completed successfully.")

    logger.info(" 📄 Files in build_dir after sphinx-build (HTML): %s", os.listdir(build_dir))

    # Nettoyage des dossiers temporaires
    for temp in [patched_source_root, patched_sphinx_source, os.path.dirname(safe_conf_path)]:
        try:
            shutil.rmtree(temp)
        except Exception:
            pass

    # Convert all HTML files to text and concatenate
    html_files = sorted(glob.glob(os.path.join(build_dir, "*.html")))
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # Extract library name from output path
    library_name = os.path.splitext(os.path.basename(output))[0]
    
    with open(output, "w", encoding="utf-8") as out:
        out.write(f"# - Complete Documentation | {library_name} -\n\n")
        for html_file in html_files:
            section = os.path.splitext(os.path.basename(html_file))[0]
            out.write(f"## {section}\n\n")
            with open(html_file, "r", encoding="utf-8") as f:
                html = f.read()
            text = html2text.html2text(html)
            out.write(text)
            out.write("\n\n---\n\n")
    logger.info(f" 📄 Combined HTML-to-text written to {output}")
    return True


def combine_text_files(build_dir: str, output_file: str, library_name: str) -> bool:
    """
    Combine all text files from the Makefile build into a single output file.
    
    Args:
        build_dir (str): Directory containing the built text files
        output_file (str): Path to the output file
        library_name (str): Name of the library for the title
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"📝 Combining text files from: {build_dir}")
        
        # Find all .txt files in the build directory
        text_files = []
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.txt'):
                    text_files.append(os.path.join(root, file))
        
        if not text_files:
            logger.warning("⚠️ No text files found in build directory")
            return False
        
        logger.info(f"📝 Found {len(text_files)} text files to combine")
        
        # Sort files to ensure consistent ordering
        text_files.sort()
        
        # Combine all text files
        combined_content = []
        combined_content.append(f"# {library_name.upper()} Documentation\n")
        combined_content.append("Generated via Sphinx Makefile\n")
        combined_content.append("=" * 50 + "\n\n")
        
        for text_file in text_files:
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    # Add file header
                    rel_path = os.path.relpath(text_file, build_dir)
                    combined_content.append(f"## {rel_path}\n")
                    combined_content.append(content)
                    combined_content.append("\n\n" + "-" * 30 + "\n\n")
            except Exception as e:
                logger.warning(f"⚠️ Could not read text file {text_file}: {e}")
                continue
        
        # Write combined content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(combined_content))
        
        logger.info(f"✅ Combined text files into: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error combining text files: {e}")
        return False


def main():
    args = parse_args()
    exclude = args.exclude.split(",") if args.exclude else []
    sphinx_source = os.path.abspath(args.sphinx_source)
    conf_path = os.path.abspath(args.conf) if args.conf else os.path.join(sphinx_source, "conf.py")
    index_path = os.path.abspath(args.index) if args.index else os.path.join(sphinx_source, "index.rst")
    source_root = os.path.abspath(args.source_root)
    library_name = args.library_name if args.library_name else os.path.basename(source_root)
    # Nouveau mode : HTML -> texte
    if hasattr(args, 'html_to_text') and args.html_to_text:
        build_html_and_convert_to_text(sphinx_source, conf_path, source_root, args.output)
        logger.info(" ✅ Sphinx HTML to text conversion successful.")
        return
    # Always use robust mode by default
    build_dir = build_markdown(sphinx_source, conf_path, source_root, robust=True)
    combine_markdown(build_dir, exclude, args.output, index_path, library_name)
    # Append all notebooks found in docs/ and doc/ (alphabetically)
    appended_notebooks = set()
    for nb_path in find_notebooks_in_doc_dirs(source_root):
        notebook_md = convert_notebook(nb_path)
        if notebook_md:
            append_notebook_markdown(args.output, notebook_md)
            appended_notebooks.add(os.path.abspath(nb_path))
    # Still allow --notebook, but avoid duplicate if already appended
    if args.notebook:
        nb_abs = os.path.abspath(args.notebook)
        if nb_abs not in appended_notebooks:
            notebook_md = convert_notebook(args.notebook)
            if notebook_md:
                append_notebook_markdown(args.output, notebook_md)
    logger.info(" ✅ Sphinx to Markdown conversion successful.")


if __name__ == "__main__":
    main()