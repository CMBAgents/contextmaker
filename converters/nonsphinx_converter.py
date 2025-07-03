import subprocess
import jupytext
import pdoc
import os
from converters import auxiliary

def create_final_markdown(input_path, output_path):
    create_markdown_files(input_path, output_path)
    combine_markdown_files(output_path, output_path)
    return None

def create_markdown_files(lib_path, output_path):
    """
    Create markdown files from the library.
    """
    for file in os.listdir(lib_path):
        if file.endswith(".ipynb"):
            jupyter_to_markdown(os.path.join(lib_path, file), output_path)
        elif file.endswith(".py") and auxiliary.has_docstrings(lib_path):
            docstrings_to_markdown(os.path.join(lib_path, file), output_path)
        elif file.endswith(".py") and auxiliary.has_source(lib_path):
            #TODO : convert the source code to txt directly
        else:
            raise ValueError("The library is not a valid documentation library")
    return None

def combine_markdown_files(lib_path, output_path):
    """
    Combine the markdown files into a single file.
    """
    os.makedirs(output_path, exist_ok=True)
    for file in os.listdir(lib_path):
        if file.endswith(".md"):
            with open(os.path.join(lib_path, file), "r") as f:
                content = f.read()
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
    return None