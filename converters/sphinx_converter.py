from converters import auxiliary
import subprocess

#TODO: reflechir a la gestion des acces a source et les path en general

def convert_sphinx_docs_to_txt(input_path, output_path):
    """
    Convert Sphinx documentation to markdown format.
    """
    #TODO : add the path to source and 
    # Convert the sphinx documentation to a markdown file
    result = subprocess.run([
    "python", "converters/markdown_builder.py",
    "--sphinx-source", "/path/to/external_lib/docs/source",
    "--output", "output.md",
    "--notebook", "notebook.ipynb"  # or any notebook you want to include
    ],
        capture_output=True,
        text=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    # Convert the markdown file to a txt file
    #TODO : the output is where we search for the markdown file
    #final_txt = auxiliary.convert_markdown_to_txt(output_path)
    # Print the result
    #print(f"Converting Sphinx documentation from {input_path} to {output_path} into a markdown file")
    return "yes"