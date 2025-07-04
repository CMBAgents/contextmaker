import os
import ast
import glob
import logging
from typing import Optional

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
        raise ValueError("❌ No valid documentation format detected.")


def has_documentation(lib_path: str) -> bool:
    """
    Check if the library contains a Sphinx documentation folder.

    Args:
        lib_path (str): Path to the library.

    Returns:
        bool: True if Sphinx files exist, else False.
    """
    docs_path = os.path.join(lib_path, 'docs')
    return (
        os.path.exists(docs_path)
        and os.path.isfile(os.path.join(docs_path, 'conf.py'))
        and os.path.isfile(os.path.join(docs_path, 'index.rst'))
    )


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