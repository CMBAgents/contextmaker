"""
Context_Maker : A tool to convert library documentation into a format optimized for ingestion by CMBAgent.

- Main script for Context_Maker -

Make sure to be located in the root of the project when running the script.
The <path_to_library> should be the root of the library.

USAGE : python contextbuilder.py --i <path_to_library> --o <path_to_output_folder>

Note : The paths can be relative or absolute and the format can be auto-detected between : sphinx, notebook, source, markdown
"""

import argparse
import os
import sys
from converters import sphinx_converter, nonsphinx_converter, auxiliary

def parse_args():
    """
    Command Line Interface
    """
    # First, we add a description of the script
    parser = argparse.ArgumentParser(
        description="Convert library docs (Sphinx, Markdown, Notebooks, source) to CMBAgent text format"
                                    )
    # Then, we add the arguments (that the user can pass to the script) namely :
    # Path to the library documentation folder or source root
    parser.add_argument(
        '--input_path', '-i', required=True,
        help='Path to the library documentation folder or source root'
                        )
    # Path to the output folder where the converted text files will be saved
    parser.add_argument(
        '--output_path', '-o', required=True,
        help='Path to output folder where converted text files will be saved'
                        )
    return parser.parse_args()

def main():
    # Necessary Arguments
    args = parse_args()
    input_path = os.path.abspath(args.input_path)
    output_path = os.path.abspath(args.output_path)

    # Check paths
    # Check input path exists and is not empty
    if not os.path.exists(input_path) or not os.listdir(input_path):
        print(f"Error: Input path {input_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    # Create output folder if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Print the arguments and the format of the documentation
    print(args)
    print(auxiliary.find_format(input_path))
    
    # Convert the documentation to a txt file

    # If the documentation exists i.e already is in sphinx format, we convert it to markdown using the builder
    if auxiliary.find_format(input_path) == 'sphinx':
        sphinx_converter.convert_sphinx_docs_to_txt(input_path, output_path)
    # If not, we convert it to markdown using jupytext (if it is a notebook), pdoc (if it is docstrings) or source code
    else:
        nonsphinx_converter.create_final_markdown(input_path, output_path)
    #TODO : MD to txt
    print("Conversion completed successfully.")
    
if __name__ == "__main__":
    main()