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
import subprocess

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
    parser.add_argument('--extension', '-e', choices=['txt', 'md'], default='txt', help='Output file extension: txt (default) or md')
    return parser.parse_args()


def markdown_to_text(md_path, txt_path):
    """
    Convert a Markdown (.md) file to plain text (.txt) using markdown and html2text.
    Args:
        md_path (str): Path to the input Markdown file.
        txt_path (str): Path to the output text file.
    """
    try:
        import markdown
        import html2text
    except ImportError:
        logger.error("markdown and html2text packages are required for Markdown to text conversion.")
        return
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html = markdown.markdown(md_content)
    text = html2text.html2text(html)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    logger.info(f"Converted {md_path} to plain text at {txt_path}")


def ensure_library_installed(library_name):
    try:
        __import__(library_name)
    except ImportError:
        logger.info(f"Library '{library_name}' not found. Attempting to install it via pip...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", library_name])
        if result.returncode != 0:
            logger.error(f"Automatic pip install failed for '{library_name}'. Please install it manually.")
            sys.exit(1)
        try:
            __import__(library_name)
        except ImportError:
            logger.error(f"Library '{library_name}' could not be imported even after pip install. Please check the library name and your environment.")
            sys.exit(1)


def main():
    try:
        args = parse_args()
        
        # Ensure target library is installed before processing
        ensure_library_installed(args.library_name)
        
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
        # Ensure CAMB is built if processing CAMB
        if args.library_name.lower() == "camb":
            auxiliary.ensure_camb_built(input_path)
            auxiliary.patch_camb_sys_exit(input_path)
        
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

        extension = args.extension

        if doc_format == 'sphinx':
            from contextmaker.converters.markdown_builder import build_markdown, combine_markdown, find_notebooks_in_doc_dirs, convert_notebook, append_notebook_markdown
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                conf_path = os.path.join(sphinx_source, "conf.py")
                index_path = os.path.join(sphinx_source, "index.rst")
                output_file = os.path.join(output_path, f"{args.library_name}.md")
                build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=False)
                import glob
                md_files = glob.glob(os.path.join(build_dir, "*.md"))
                if not md_files:
                    logger.warning(" ⚠️ Sphinx build with original conf.py failed or produced no markdown. Falling back to minimal configuration...")
                    build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=True)
                combine_markdown(build_dir, [], output_file, index_path, args.library_name)
                appended_notebooks = set()
                for nb_path in find_notebooks_in_doc_dirs(input_path):
                    notebook_md = convert_notebook(nb_path)
                    if notebook_md:
                        append_notebook_markdown(output_file, notebook_md)
                        appended_notebooks.add(os.path.abspath(nb_path))
                success = True
            else:
                success = False
        else:
            success = nonsphinx_converter.create_final_markdown(input_path, output_path, args.library_name)
        
        if success:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file if doc_format == 'sphinx' else output_path}")
            if extension == 'txt' and output_file is not None:
                txt_file = os.path.splitext(output_file)[0] + ".txt"
                markdown_to_text(output_file, txt_file)
                # Delete the markdown file after successful text conversion
                if os.path.exists(txt_file):
                    try:
                        os.remove(output_file)
                        logger.info(f"Deleted markdown file after text conversion: {output_file}")
                    except Exception as e:
                        logger.warning(f"Could not delete markdown file: {output_file}. Error: {e}")
                return txt_file
            elif output_file is not None:
                return output_file
            else:
                return None
        else:
            logger.warning(" ⚠️ Conversion completed with warnings or partial results.")

        # At the very end, delete the conversion.log file if it exists
        log_path = os.path.join(os.getcwd(), "conversion.log")
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
                logger.info(f"Deleted log file: {log_path}")
            except Exception as e:
                logger.warning(f"Could not delete log file: {log_path}. Error: {e}")

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        sys.exit(1)


def make(library_name, output_path=None, input_path=None, extension='txt'):
    """
    Convert a library's documentation to text or markdown format (programmatic API).
    Args:
        library_name (str): Name of the library to convert (e.g., "pixell", "numpy").
        output_path (str, optional): Output directory. Defaults to ~/your_context_library/.
        input_path (str, optional): Manual path to library (overrides automatic search).
        extension (str, optional): Output file extension: 'txt' (default) or 'md'.
    Returns:
        str: Path to the generated documentation file, or None if failed.
    """
    try:
        # Ensure target library is installed before processing
        ensure_library_installed(library_name)
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
        # Ensure CAMB is built if processing CAMB
        if library_name.lower() == "camb":
            auxiliary.ensure_camb_built(input_path)
            auxiliary.patch_camb_sys_exit(input_path)

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
            from contextmaker.converters.markdown_builder import build_markdown, combine_markdown, find_notebooks_in_doc_dirs, convert_notebook, append_notebook_markdown
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                conf_path = os.path.join(sphinx_source, "conf.py")
                index_path = os.path.join(sphinx_source, "index.rst")
                output_file = os.path.join(output_path, f"{library_name}.md")
                build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=False)
                import glob
                md_files = glob.glob(os.path.join(build_dir, "*.md"))
                if not md_files:
                    logger.warning(" ⚠️ Sphinx build with original conf.py failed or produced no markdown. Falling back to minimal configuration...")
                    build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=True)
                combine_markdown(build_dir, [], output_file, index_path, library_name)
                appended_notebooks = set()
                for nb_path in find_notebooks_in_doc_dirs(input_path):
                    notebook_md = convert_notebook(nb_path)
                    if notebook_md:
                        append_notebook_markdown(output_file, notebook_md)
                        appended_notebooks.add(os.path.abspath(nb_path))
                success = True
            else:
                success = False
                output_file = None
        else:
            success = nonsphinx_converter.create_final_markdown(input_path, output_path, library_name)
            output_file = os.path.join(output_path, f"{library_name}.md")

        if success:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file}")
            if extension == 'txt' and output_file is not None:
                txt_file = os.path.splitext(output_file)[0] + ".txt"
                markdown_to_text(output_file, txt_file)
                # Delete the markdown file after successful text conversion
                if os.path.exists(txt_file):
                    try:
                        os.remove(output_file)
                        logger.info(f"Deleted markdown file after text conversion: {output_file}")
                    except Exception as e:
                        logger.warning(f"Could not delete markdown file: {output_file}. Error: {e}")
                return txt_file
            elif output_file is not None:
                return output_file
            else:
                return None
        else:
            logger.warning(" ⚠️ Conversion completed with warnings or partial results.")
            return None

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    main()