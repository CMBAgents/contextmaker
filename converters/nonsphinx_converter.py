import subprocess
import os
import ast
from converters import auxiliary

def create_final_markdown(input_path, output_path):
    """
    Create the final markdown file from the library.
    """
    # We create a temporary output path to store the markdown files
    temp_output_path = create_markdown_files(input_path, output_path)
    # We combine the markdown files into a single file
    combine_markdown_files(temp_output_path, output_path)
    #TODO : Suppress the temp folder
    return None

def create_markdown_files(lib_path, output_path):
    """
    Create markdown files from the library.
    """
    # We create a temporary output path to store the markdown files
    temp_output_path = output_path + "/temp"
    os.makedirs(temp_output_path, exist_ok=True)
    # We create the markdown files
    for file in os.listdir(lib_path):
        if file.endswith(".ipynb"):
            jupyter_to_markdown(os.path.join(lib_path, file), temp_output_path)
        elif file.endswith(".py") and auxiliary.has_docstrings(lib_path):
            docstrings_to_markdown(os.path.join(lib_path, file), temp_output_path)
        elif file.endswith(".py") and auxiliary.has_source(lib_path):
            source_to_markdown(os.path.join(lib_path, file), temp_output_path)
        else:
            raise ValueError("The library is not a valid documentation library")
    return temp_output_path

def combine_markdown_files(temp_output_path, output_path):
    """
    Combine the markdown files into a single file.
    """
    os.makedirs(output_path, exist_ok=True)
    for file in os.listdir(temp_output_path):
        #TODO : Separator between the different files
        if file.endswith(".md", ".txt"):
            # We read the markdown file in the temporary output path
            with open(os.path.join(temp_output_path, file), "r") as f:
                content = f.read()
            # We write the markdown file to the output path
            with open(os.path.join(output_path, file), "w") as f:
                f.write(content)
    return None

def jupyter_to_markdown(file_path, output_path):
    """
    Convert a jupyter notebook to a markdown file.
    """
    cmd = ["jupytext", "--to", "md", file_path, "-o", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Jupytext error:", result.stderr)
    else:
        print("Notebook converted to markdown.")
    return None

def docstrings_to_markdown(file_path, output_path):
    """
    Extract all docstrings from a Python file and write them to a markdown file.
    """
    with open(file_path, "r") as f:
        source = f.read()

    # Parse the source code into an AST
    tree = ast.parse(source, filename=file_path)

    docstrings = []

    # Get the module-level docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docstrings.append(f"# Module docstring\n\n{module_doc}\n")

    # Walk through all nodes to find class and function docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if doc:
                if isinstance(node, ast.ClassDef):
                    header = f"## Class `{node.name}`"
                else:
                    header = f"### Function `{node.name}`"
                docstrings.append(f"{header}\n\n{doc}\n")

    # Write all collected docstrings to the output file
    with open(output_path, "w") as f:
        f.write("\n".join(docstrings))
    return None

def source_to_markdown(file_path, output_path):
    """
    Convert a python file to a markdown file.
    """
    # We read the python file
    with open(file_path, "r") as f:
        content = f.read()
    # We write the content of the python file to the output path
    with open(output_path, "w") as f:
        f.write(content)