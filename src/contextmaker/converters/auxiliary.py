import os
import ast
import glob
import logging
import platform
import subprocess
import sys

logger = logging.getLogger(__name__)


def find_format(lib_path: str) -> str:
    """
    Detect the documentation format of a given library.

    Args:
        lib_path (str): Path to the root of the library.

    Returns:
        str: One of ['sphinx', 'notebook', 'docstrings', 'source'].

    Raises:
        ValueError: If no valid format is detected.
    """
    if has_documentation(lib_path):
        logger.info(" 📚 Detected Sphinx-style documentation.")
        return 'sphinx'
    elif has_notebook(lib_path):
        logger.info(" 📒 Detected Jupyter notebooks.")
        return 'notebook'
    elif has_docstrings(lib_path):
        logger.info(" 📄 Detected inline docstrings.")
        return 'docstrings'
    elif has_source(lib_path):
        logger.info(" 💻 Detected raw source code.")
        return 'source'
    else:
        # For installed packages without documentation, try to extract docstrings from source
        logger.info(" 📦 Detected installed package, extracting docstrings from source code.")
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
    if has_documentation(lib_path):
        return False

    notebook_dir = os.path.join(lib_path, 'notebooks')
    if os.path.exists(notebook_dir):
        notebooks = glob.glob(os.path.join(notebook_dir, '*.ipynb'))
        return len(notebooks) > 0
    return False


def has_docstrings(file_path: str) -> bool:
    """
    Check if the Python file contains docstrings.

    Args:
        file_path (str): Path to a .py file.

    Returns:
        bool: True if at least one docstring is found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        return False

    if ast.get_docstring(tree):
        return True

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node):
                return True
    return False


def has_source(lib_path: str) -> bool:
    """
    Check if the library has source code but no other documentation.

    Args:
        lib_path (str): Path to the library.

    Returns:
        bool: True if only source code is found.
    """
    if not has_documentation(lib_path) and not has_notebook(lib_path):
        py_files = [
            os.path.join(dp, f)
            for dp, _, filenames in os.walk(lib_path)
            for f in filenames if f.endswith('.py')
        ]
        return any(has_docstrings(fp) for fp in py_files) is False
    return False


def find_library_path(library_name: str) -> str | None:
    """
    Find the library path by searching in common locations.
    - Prefer Sphinx documentation (doc/ or docs/ with conf.py and index.rst).
    - When searching from the home directory and its subfolders, if no Sphinx doc is found after searching up to four directory levels deep, accept a directory with the correct name even if it doesn't have Sphinx docs.
    - Do NOT do this for site-packages or pip-installed locations.
    Args:
        library_name (str): Name of the library to find.
    Returns:
        str | None: Path to the library if found, None otherwise.
    """
    import site
    import sys

    # Common search paths
    search_paths = []

    # 1. Current working directory and subdirectories
    search_paths.append(os.getcwd())

    # 2. User's home directory and common subdirectories
    home = os.path.expanduser("~")
    home_subdirs = [
        home,
        os.path.join(home, "Documents"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Projects"),
        os.path.join(home, "repos"),
        os.path.join(home, "workspace"),
        os.path.join(home, "code"),
    ]
    search_paths.extend(home_subdirs)

    # 3. Python site-packages directories
    site_package_paths = []
    for site_dir in site.getsitepackages():
        site_package_paths.append(site_dir)
    # 4. User site-packages
    user_site = site.getusersitepackages()
    if user_site:
        site_package_paths.append(user_site)
    # 5. Virtual environment site-packages (if in a venv)
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_site = os.path.join(sys.prefix, 'lib', 'python*', 'site-packages')
        site_package_paths.extend(glob.glob(venv_site))
    # 6. Conda environments
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        conda_site = os.path.join(conda_prefix, 'lib', 'python*', 'site-packages')
        site_package_paths.extend(glob.glob(conda_site))
    search_paths.extend(site_package_paths)

    # Helper to check for Sphinx doc - use the existing find_sphinx_source function
    def has_sphinx_doc(lib_path: str) -> str | None:
        sphinx_source = find_sphinx_source(lib_path)
        if sphinx_source:
            logger.debug(f"✅ Sphinx docs found in: {sphinx_source}")
            return sphinx_source
        logger.debug(f"❌ No Sphinx docs found in: {lib_path}")
        return None

    # Helper to check if a path is under home or its subfolders
    def is_under_home(path: str) -> bool:
        return any(os.path.commonpath([os.path.abspath(path), os.path.abspath(h)]) == os.path.abspath(h) for h in home_subdirs)

    # Track if we found a non-Sphinx match under home (for fallback)
    nonsphinx_candidate = None
    nonsphinx_candidate_depth = float('inf')

    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue

        logger.debug(f"🔍 Searching in: {search_path}")

        # Look for exact match first
        exact_path = os.path.join(search_path, library_name)
        if os.path.exists(exact_path):
            logger.debug(f"📁 Found exact match: {exact_path}")
            doc_path = has_sphinx_doc(exact_path)
            if doc_path:
                logger.info(f"✅ Found library '{library_name}' with Sphinx docs at: {exact_path}")
                return exact_path
            # If under home, record as possible fallback
            if is_under_home(exact_path):
                depth = os.path.relpath(exact_path, home).count(os.sep)
                if depth < nonsphinx_candidate_depth:
                    nonsphinx_candidate = exact_path
                    nonsphinx_candidate_depth = depth
            else:
                logger.debug(f"❌ No Sphinx docs found in: {exact_path}")

        # Look in subdirectories
        for root, dirs, files in os.walk(search_path):
            for dir_name in dirs:
                if dir_name.lower() == library_name.lower():
                    full_path = os.path.join(root, dir_name)
                    logger.debug(f"📁 Found subdirectory match: {full_path}")
                    doc_path = has_sphinx_doc(full_path)
                    if doc_path:
                        logger.info(f"✅ Found library '{library_name}' with Sphinx docs at: {full_path}")
                        return full_path
                    # If under home, record as possible fallback
                    if is_under_home(full_path):
                        depth = os.path.relpath(full_path, home).count(os.sep)
                        if depth < nonsphinx_candidate_depth:
                            nonsphinx_candidate = full_path
                            nonsphinx_candidate_depth = depth
                    else:
                        logger.debug(f"❌ No Sphinx docs found in: {full_path}")

    # Fallback: if we searched under home and found a non-Sphinx candidate within 4 levels, return it
    if nonsphinx_candidate is not None and nonsphinx_candidate_depth <= 4:
        logger.warning(f"⚠️ No Sphinx docs found, but returning non-Sphinx library at: {nonsphinx_candidate} (depth {nonsphinx_candidate_depth})")
        return nonsphinx_candidate

    logger.error(f"❌ Library '{library_name}' with Sphinx documentation not found in common locations")
    return None


def get_default_output_path() -> str:
    """
    Get the default output path in user's home directory.
    
    Returns:
        str: Default output path.
    """
    home = os.path.expanduser("~")
    default_path = os.path.join(home, "your_context_library")
    return default_path


def convert_markdown_to_txt(output_folder: str, library_name: str) -> str:
    """
    Convert the output.md file in the output folder to a .txt file with library name.

    Args:
        output_folder (str): Folder containing output.md file.
        library_name (str): Name of the library for the txt filename.

    Returns:
        str: Path to the created .txt file.
    """
    md_path = os.path.join(output_folder, "output.md")
    if not os.path.isfile(md_path):
        logger.error(f"Markdown file does not exist: {md_path}")
        raise FileNotFoundError(md_path)

    with open(md_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    txt_filename = f"{library_name}.txt"
    txt_path = os.path.join(output_folder, txt_filename)

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(content)

    logger.info(f"✅ Markdown converted to text at: {txt_path}")
    return txt_path


def find_library_file(camb_dir, libname):
    """
    Recursively search for the Fortran library file under camb_dir.
    Returns the first match or None if not found.
    """
    matches = glob.glob(os.path.join(camb_dir, '**', libname), recursive=True)
    return matches[0] if matches else None


def ensure_camb_built(camb_dir: str):
    """
    Ensure the CAMB Fortran library is built. If not, build it automatically.
    Args:
        camb_dir (str): Path to the CAMB source directory (where setup.py is).
    Raises:
        RuntimeError: If the build fails or setup.py is missing.
    """
    libname = "cambdll.dll" if platform.system() == "Windows" else "camblib.so"
    libpath = find_library_file(camb_dir, libname)
    if not libpath:
        setup_py = os.path.join(camb_dir, "setup.py")
        if not os.path.isfile(setup_py):
            raise RuntimeError(f"setup.py not found in {camb_dir}")
        logger.info(f"Building CAMB Fortran library in {camb_dir}...")
        result = subprocess.run([sys.executable, "setup.py", "make"], cwd=camb_dir)
        # Search again after build
        libpath = find_library_file(camb_dir, libname)
        if result.returncode != 0 or not libpath:
            logger.error("Failed to build CAMB Fortran library. Please check your Fortran compiler and dependencies.")
            raise RuntimeError("Failed to build CAMB Fortran library. Please check your Fortran compiler and dependencies.")
        logger.info(f"CAMB Fortran library built successfully at {libpath}.")
    else:
        logger.info(f"CAMB Fortran library already built at {libpath}.")

# --- CAMB sys.exit patching utility ---

def patch_camb_sys_exit(camb_dir: str):
    """
    Recursively replace sys.exit( with raise ImportError( in all .py files under camb_dir, except excluded files.
    Args:
        camb_dir (str): Path to the CAMB source directory.
    """
    import os
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
        if not os.path.exists(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(".py"):
                    fullpath = os.path.join(dirpath, filename)
                    if should_patch(fullpath):
                        patch_sys_exit_in_file(fullpath)