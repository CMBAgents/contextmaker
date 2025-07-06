import subprocess
import os
import sys
import ast
import shutil
import logging
from contextmaker.converters import auxiliary

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_final_markdown(input_path, output_path):
    """
    Create the final markdown file from the library documentation or source files.

    This function:
    - Creates individual markdown files for each relevant input file (notebooks, Python files with docstrings or source).
    - Combines all generated markdown files into a single 'final_output.md' file.
    - Deletes the temporary folder used to store intermediate markdown files.

    Parameters:
        input_path (str): Path to the library or documentation source.
        output_path (str): Path where the final markdown file will be saved.
    """
    temp_output_path = create_markdown_files(input_path, output_path)
    combine_markdown_files(temp_output_path, output_path)

    # Remove the temporary directory after combining files
    shutil.rmtree(temp_output_path, ignore_errors=True)
    logger.info(f"Temporary folder '{temp_output_path}' removed after processing.")

def create_markdown_files(lib_path, output_path):
    """
    Generate markdown files from the library source files.

    Processes all files in lib_path, converting notebooks, extracting docstrings
    or copying source code into markdown files stored in a temporary directory.

    Parameters:
        lib_path (str): Path to the source library or documentation.
        output_path (str): Path where the temporary markdown files will be saved.

    Returns:
        str: Path to the temporary directory containing the markdown files.
    """
    temp_output_path = os.path.join(output_path, "temp")
    os.makedirs(temp_output_path, exist_ok=True)

    for file in os.listdir(lib_path):
        full_path = os.path.join(lib_path, file)
        if file.endswith(".ipynb"):
            jupyter_to_markdown(full_path, temp_output_path)
        elif file.endswith(".py") and auxiliary.has_docstrings(full_path):
            docstrings_to_markdown(full_path, temp_output_path)
        elif file.endswith(".py") and auxiliary.has_source(lib_path):
            source_to_markdown(full_path, temp_output_path)
        else:
            raise ValueError("The library is not a valid documentation library")

    return temp_output_path

def combine_markdown_files(temp_output_path, output_path):
    """
    Combine all markdown files in the temporary directory into a single markdown file.

    Inserts separators and filenames as headers to clarify source files.

    Parameters:
        temp_output_path (str): Path to the temporary markdown files.
        output_path (str): Path where the combined markdown file will be saved.
    """
    os.makedirs(output_path, exist_ok=True)
    combined_file_path = os.path.join(output_path, "final_output.md")

    with open(combined_file_path, "w", encoding="utf-8") as combined_file:
        for file in sorted(os.listdir(temp_output_path)):
            if file.endswith((".md", ".txt")):
                file_path = os.path.join(temp_output_path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_file.write(f"\n\n---\n\n# {file}\n\n")
                    combined_file.write(content)

    logger.info(f"All markdown files combined into: {combined_file_path}")

def jupyter_to_markdown(file_path, output_path):
    """
    Convert a Jupyter notebook (.ipynb) to a markdown file using jupytext.

    Parameters:
        file_path (str): Path to the Jupyter notebook.
        output_path (str): Directory to save the generated markdown file.
    """
    cmd = ["jupytext", "--to", "md", file_path, "-o", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Jupytext error: %s", result.stderr)
    else:
        logger.info("Notebook converted to markdown: %s", file_path)

def docstrings_to_markdown(file_path, output_path):
    """
    Extract docstrings from a Python file and write them to a markdown file.

    Extracts module, class, and function docstrings and formats them with markdown headers.

    Parameters:
        file_path (str): Path to the Python source file.
        output_path (str): Directory to save the markdown file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=file_path)
    docstrings = []

    module_doc = ast.get_docstring(tree)
    if module_doc:
        docstrings.append(f"# Module docstring\n\n{module_doc}\n")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if doc:
                if isinstance(node, ast.ClassDef):
                    header = f"## Class `{node.name}`"
                else:
                    header = f"### Function `{node.name}`"
                docstrings.append(f"{header}\n\n{doc}\n")

    output_file = os.path.join(output_path, os.path.basename(file_path).replace(".py", ".md"))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(docstrings))

def source_to_markdown(file_path, output_path):
    """
    Convert a Python source file to markdown by copying its content as-is.

    Parameters:
        file_path (str): Path to the Python source file.
        output_path (str): Directory to save the markdown file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    output_file = os.path.join(output_path, os.path.basename(file_path).replace(".py", ".md"))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)