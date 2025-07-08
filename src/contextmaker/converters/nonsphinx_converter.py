import subprocess
import os
import sys
import ast
import shutil
import logging
from contextmaker.converters import auxiliary
import html2text

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_final_markdown(input_path, output_path, library_name=None):
    """
    Create the final text file from the library documentation or source files.

    This function:
    - Creates individual markdown files for each relevant input file (notebooks, Python files with docstrings or source).
    - Combines all generated markdown files into a single '<library_name>.txt' file as plain text.
    - Deletes the temporary folder used to store intermediate markdown files.

    Parameters:
        input_path (str): Path to the library or documentation source.
        output_path (str): Path where the final text file will be saved.
        library_name (str): Name of the library for the output file.
    """
    temp_output_path = create_markdown_files(input_path, output_path)
    if library_name is None:
        library_name = os.path.basename(os.path.normpath(input_path))
    combine_markdown_files_to_txt(temp_output_path, output_path, library_name)
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

    # Track if we found any valid files
    found_files = False
    
    # Recursively search for files
    for root, dirs, files in os.walk(lib_path):
        # Skip common directories that don't contain documentation
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules']]
        
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, lib_path)
            
            if file.endswith(".ipynb"):
                jupyter_to_markdown(full_path, temp_output_path)
                found_files = True
            elif file.endswith(".py") and auxiliary.has_docstrings(full_path):
                docstrings_to_markdown(full_path, temp_output_path)
                found_files = True
            elif file.endswith(".py") and auxiliary.has_source(lib_path):
                source_to_markdown(full_path, temp_output_path)
                found_files = True
    
    if not found_files:
        logger.warning("No documentation files found in the library. This may be a library without docstrings or documentation.")
        # Create a basic documentation file from README or similar
        create_basic_documentation(lib_path, temp_output_path)
    
    return temp_output_path

def combine_markdown_files_to_txt(temp_output_path, output_path, library_name):
    """
    Combine all markdown files in the temporary directory into a single text file named <library_name>.txt.
    For non-Sphinx projects, preserve the Markdown formatting exactly as in the .md files.
    """
    os.makedirs(output_path, exist_ok=True)
    combined_file_path = os.path.join(output_path, f"{library_name}.txt")
    with open(combined_file_path, "w", encoding="utf-8") as combined_file:
        # Add the global title like in the Sphinx converter
        combined_file.write(f"# - Complete Documentation | {library_name} -\n\n")
        
        for file in sorted(os.listdir(temp_output_path)):
            if file.endswith((".md", ".txt")):
                file_path = os.path.join(temp_output_path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Write a section separator and filename
                    combined_file.write(f"\n\n---\n\n# {file}\n\n")
                    combined_file.write(content)
    logger.info(f"All documentation combined into: {combined_file_path}")

def jupyter_to_markdown(file_path, output_path):
    """
    Convert a Jupyter notebook (.ipynb) to a markdown file using jupytext.

    Parameters:
        file_path (str): Path to the Jupyter notebook.
        output_path (str): Directory to save the generated markdown file.
    """
    # Construct the output .md file path in the output directory
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    md_file_path = os.path.join(output_path, base_name + ".md")
    cmd = ["jupytext", "--to", "md", file_path, "-o", md_file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Jupytext error: %s", result.stderr)
    else:
        logger.info("Notebook converted to markdown: %s", md_file_path)

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

def create_basic_documentation(lib_path, output_path):
    """
    Create basic documentation from README files or other common documentation files.

    Parameters:
        lib_path (str): Path to the library.
        output_path (str): Directory to save the documentation file.
    """
    # Look for common documentation files
    doc_files = ['README.md', 'README.rst', 'README.txt', 'CHANGELOG.md', 'CHANGELOG.rst']
    
    for doc_file in doc_files:
        doc_path = os.path.join(lib_path, doc_file)
        if os.path.exists(doc_path):
            output_file = os.path.join(output_path, f"basic_documentation_{doc_file}")
            shutil.copy2(doc_path, output_file)
            logger.info(f"Copied {doc_file} to basic documentation")
            return
    
    # If no documentation files found, create a basic summary
    output_file = os.path.join(output_path, "basic_documentation.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Basic Documentation for {os.path.basename(lib_path)}\n\n")
        f.write("This library was processed but no structured documentation was found.\n")
        f.write("The library may contain source code without docstrings or may require special setup for documentation generation.\n")
    
    logger.info("Created basic documentation summary")