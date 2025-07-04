"""
Context_Maker: A tool to convert library documentation into a format optimized for ingestion by CMBAgent.

Usage:
    python contextbuilder.py --i <path_to_library> --o <path_to_output_folder>

Notes:
    - Run the script from the root of the project.
    - <path_to_library> should be the root directory of the target library.
    - Supported formats (auto-detected): sphinx, notebook, source, markdown.
"""

import argparse
import os
import sys
import logging
from converters import sphinx_converter, nonsphinx_converter, auxiliary

# Set up the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("conversion.log")
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert library docs (Sphinx, Markdown, Notebooks, source) to CMBAgent text format"
    )
    parser.add_argument('--input_path', '-i', required=True, help='Path to the library documentation folder')
    parser.add_argument('--output_path', '-o', required=True, help='Path to the output folder for converted files')
    return parser.parse_args()


def main():
    try:
        args = parse_args()
        input_path = os.path.abspath(args.input_path)
        output_path = os.path.abspath(args.output_path)

        if not os.path.exists(input_path):
            logger.error(f"Input path '{input_path}' does not exist.")
            sys.exit(1)

        if not os.listdir(input_path):
            logger.error(f"Input path '{input_path}' is empty.")
            sys.exit(1)

        os.makedirs(output_path, exist_ok=True)

        doc_format = auxiliary.find_format(input_path)
        logger.info(f" 📚 Detected documentation format: {doc_format}")

        if doc_format == 'sphinx':
            success = sphinx_converter.convert_sphinx_docs_to_txt(input_path, output_path)
        else:
            success = nonsphinx_converter.create_final_markdown(input_path, output_path)
        #TODO : add the md to txt
        if success:
            logger.info(" ✅ Conversion completed successfully.")
        else:
            logger.warning(" ⚠️ Conversion completed with warnings or partial results.")

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()