"""
Notebook utilities for contextmaker.
Contains functions for finding and converting Jupyter notebooks.
"""

import os
import glob
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)


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
        logger.debug(f"Using recursive search for notebooks in {library_root}")
        return find_all_notebooks_recursive(library_root)
    
    # Original behavior for backward compatibility
    logger.debug(f"Using legacy search in docs/, doc/, docs/source/ for {library_root}")
    candidates = []
    for doc_dir in ["docs", "doc", "docs/source"]:
        abs_doc_dir = os.path.join(library_root, doc_dir)
        if os.path.isdir(abs_doc_dir):
            found = glob.glob(os.path.join(abs_doc_dir, "*.ipynb"))
            logger.debug(f"Notebooks in {doc_dir}: {found}")
            candidates.extend(found)
    
    abs_candidates = sorted([os.path.abspath(nb) for nb in candidates])
    if abs_candidates:
        logger.debug(f"Notebooks found: {abs_candidates}")
    else:
        logger.debug(f"No notebooks found in docs/, doc/, or docs/source/ under {library_root}.")
    return abs_candidates


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
    
    logger.debug(f"Starting recursive notebook search in: {library_root}")
    logger.debug(f"Excluding patterns: {sorted(all_exclusions)}")
    
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
                logger.debug(f"Found notebook: {relative_path}")
    
    # Sort by relative path for consistent ordering
    candidates.sort(key=lambda x: x[1])
    
    # Extract just the full paths
    notebook_paths = [c[0] for c in candidates]
    
    logger.debug(f"Search completed: {total_dirs_scanned} directories, {total_files_scanned} files scanned")
    logger.debug(f"Found {len(notebook_paths)} notebooks")
    
    return notebook_paths


def convert_notebook(nb_path):
    """
    Convert Jupyter notebook to markdown using jupytext.
    
    Args:
        nb_path (str): Path to the Jupyter notebook file
        
    Returns:
        str | None: Path to the generated markdown file, or None if conversion failed
    """
    logger.debug(f"Converting notebook: {nb_path}")
    
    if not shutil.which("jupytext"):
        logger.error("jupytext is required to convert notebooks.")
        return None
    
    md_path = os.path.splitext(nb_path)[0] + ".md"
    cmd = ["jupytext", "--to", "md", "--opt", "notebook_metadata_filter=-all", nb_path]
    
    logger.debug("Running jupytext conversion...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Failed to convert notebook: {result.stderr}")
        return None
    
    if not os.path.exists(md_path):
        logger.error(f"Expected markdown file {md_path} not found after conversion.")
        return None
    
    logger.debug(f"Notebook converted to {md_path}")
    return md_path


def append_notebook_markdown(output_file, notebook_md):
    """
    Append notebook markdown content to an existing output file.
    
    Args:
        output_file (str): Path to the output file to append to
        notebook_md (str): Path to the notebook markdown file to append
    """
    logger.info(f"Appending notebook {notebook_md} to {output_file}")
    
    try:
        with open(output_file, "a", encoding="utf-8") as out, open(notebook_md, encoding="utf-8") as nb_md:
            out.write("\n\n# Notebook\n\n---\n\n")
            out.write(nb_md.read())
        logger.info(f"Notebook appended: {notebook_md}")
    except Exception as e:
        logger.error(f"Failed to append notebook {notebook_md}: {e}")
