"""
Context_Maker: A tool to convert library documentation into a format optimized for ingestion by CMBAgent.

Usage:
    contextmaker <library_name>
    or
    contextmaker pixell --input_path /path/to/library/source
    or
    python contextmaker/contextmaker.py --i <path_to_library> --o <path_to_output_folder>

Notes:
    - Run the script from the root of the project.
    - <path_to_library> should be the root directory of the target library.
    - Supported formats (auto-detected): sphinx, notebook, source, markdown.
"""

import argparse
import os
import sys
import logging
from contextmaker.converters import nonsphinx_converter, auxiliary

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
        description="Convert library documentation to text format. Automatically finds libraries on your system."
    )
    parser.add_argument('library_name', help='Name of the library to convert (e.g., "pixell", "numpy")')
    parser.add_argument('--output', '-o', help='Output path (default: ~/contextmaker_output/)')
    parser.add_argument('--input_path', '-i', help='Manual path to library (overrides automatic search)')
    return parser.parse_args()


def main():
    try:
        args = parse_args()
        
        # Determine input path
        if args.input_path:
            # Manual path provided
            input_path = os.path.abspath(args.input_path)
            logger.info(f"📁 Using manual path: {input_path}")
        else:
            # Automatic search
            logger.info(f"🔍 Searching for library '{args.library_name}'...")
            input_path = auxiliary.find_library_path(args.library_name)
            if not input_path:
                logger.error(f"❌ Library '{args.library_name}' not found. Try specifying the path manually with --input_path")
                sys.exit(1)
        
        # Determine output path
        if args.output:
            output_path = os.path.abspath(args.output)
        else:
            output_path = auxiliary.get_default_output_path()
        
        logger.info(f"📁 Input path: {input_path}")
        logger.info(f"📁 Output path: {output_path}")

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
            # Always use the HTML->text workflow for complete documentation
            from contextmaker.converters.markdown_builder import build_html_and_convert_to_text
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                conf_path = os.path.join(sphinx_source, "conf.py")
                output_file = os.path.join(output_path, f"{args.library_name}.txt")
                success = build_html_and_convert_to_text(sphinx_source, conf_path, input_path, output_file)
                
                # If sphinx build fails, fallback to docstring extraction
                if not success:
                    logger.warning(" ⚠️ Sphinx build failed. Falling back to docstring extraction from source code...")
                    success = nonsphinx_converter.create_final_markdown(input_path, output_path, args.library_name)
            else:
                success = False
        else:
            success = nonsphinx_converter.create_final_markdown(input_path, output_path, args.library_name)
        
        if success:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file if doc_format == 'sphinx' else output_path}")
        else:
            logger.warning(" ⚠️ Conversion completed with warnings or partial results.")

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        sys.exit(1)


def convert(library_name, output_path=None, input_path=None):
    """
    Convert a library's documentation to text format (programmatic API).

    Args:
        library_name (str): Name of the library to convert (e.g., "pixell", "numpy").
        output_path (str, optional): Output directory. Defaults to ~/your_context_library/.
        input_path (str, optional): Manual path to library (overrides automatic search).

    Returns:
        str: Path to the generated documentation file, or None if failed.
    """
    try:
        # Determine input path
        if input_path:
            input_path = os.path.abspath(input_path)
            logger.info(f"📁 Using manual path: {input_path}")
        else:
            logger.info(f"🔍 Searching for library '{library_name}'...")
            input_path = auxiliary.find_library_path(library_name)
            if not input_path:
                logger.error(f"❌ Library '{library_name}' not found. Try specifying the path manually with input_path.")
                return None

        # Determine output path
        if output_path:
            output_path = os.path.abspath(output_path)
        else:
            output_path = auxiliary.get_default_output_path()

        logger.info(f"📁 Input path: {input_path}")
        logger.info(f"📁 Output path: {output_path}")

        if not os.path.exists(input_path):
            logger.error(f"Input path '{input_path}' does not exist.")
            return None

        if not os.listdir(input_path):
            logger.error(f"Input path '{input_path}' is empty.")
            return None

        os.makedirs(output_path, exist_ok=True)

        doc_format = auxiliary.find_format(input_path)
        logger.info(f" 📚 Detected documentation format: {doc_format}")

        if doc_format == 'sphinx':
            from contextmaker.converters.markdown_builder import build_html_and_convert_to_text
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                conf_path = os.path.join(sphinx_source, "conf.py")
                output_file = os.path.join(output_path, f"{library_name}.txt")
                success = build_html_and_convert_to_text(sphinx_source, conf_path, input_path, output_file)
                if not success:
                    logger.warning(" ⚠️ Sphinx build failed. Falling back to docstring extraction from source code...")
                    success = nonsphinx_converter.create_final_markdown(input_path, output_path, library_name)
                    output_file = os.path.join(output_path, f"{library_name}.txt")
            else:
                success = False
                output_file = None
        else:
            success = nonsphinx_converter.create_final_markdown(input_path, output_path, library_name)
            output_file = os.path.join(output_path, f"{library_name}.txt")

        if success:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file}")
            return output_file
        else:
            logger.warning(" ⚠️ Conversion completed with warnings or partial results.")
            return None

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    main()