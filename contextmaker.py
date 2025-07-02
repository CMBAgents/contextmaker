"""
Context_Maker : A tool to convert library documentation into a format optimized for ingestion by CMBAgent.

- Main script for ContextMaker -

USAGE : python contextbuilder.py --i <path_to_library> --o <path_to_output_folder>

Note : The paths can be relative or absolute and the format can be auto-detected between : sphinx, notebook, source, markdown
"""

import argparse
import os
import sys
from converters import sphinx_converter

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
    # Check input path exists
    if not os.path.exists(input_path):
        print(f"Error: Input path {input_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    # Create output folder if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    print(args)
    
    # Convert the documentation to a txt file
    if sphinx_converter.convert_sphinx_docs_to_txt(input_path, output_path) is None:
        print(f"Error: Unsupported format '{input_path}'", file=sys.stderr)
        sys.exit(1)
    else:
        print("Conversion completed successfully.")
    
if __name__ == "__main__":
    main()