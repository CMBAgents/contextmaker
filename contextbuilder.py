"""
Main script for ContextMaker
Convert various library documentation formats into 
clean text files optimized for ingestion by CMBAgent.
"""

import argparse
import os
import sys
from converters import auxiliary, sphinx_converter, notebook_converter, source_parser

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
    # Format of the input documentation (auto-detect, sphinx, notebook, source, markdown)
    parser.add_argument(
        '--format', '-f', choices=['auto', 'sphinx', 'notebook', 'source', 'markdown'], default='auto',
        help='Input documentation format to process (default: auto-detect)'
                        )
    # Print logs
    parser.add_argument(
        '--logs', '-l', action='store_true',
        help='Print detailed logs'
                        )
    return parser.parse_args()

def main():
    """
    Main function
    """
    # Arguments
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
    
    '''# Check format (Auto-detect format if needed)
    doc_format = args.format
    if doc_format == 'auto':
        doc_format = auxiliary.find_format(input_path)
        if args.verbose:
            print(f"Auto-detected format: {doc_format}")
    '''
    
    # Decide the right converter to use
    '''
    if doc_format == 'sphinx':
        # todo : add function to convert sphinx docs to text files
    elif doc_format == 'notebook':
        # todo : add function to convert notebooks to text files
    elif doc_format == 'markdown':
        # todo : add function to convert markdown to text files
    elif doc_format == 'source':
        # todo : add function to parse source code to text files
    else:
        print(f"Error: Unsupported format '{doc_format}'", file=sys.stderr)
        sys.exit(1)
    '''
    
    # Print success message
    print("Conversion completed successfully.")

if __name__ == "__main__":
    main()