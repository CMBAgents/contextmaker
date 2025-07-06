import subprocess
import os
import sys
import logging
from contextmaker.converters import auxiliary

logger = logging.getLogger(__name__)


def convert_sphinx_docs_to_txt(input_path: str, output_path: str) -> bool:
    """
    Convert Sphinx documentation to a Markdown file, then optionally to text.

    Args:
        input_path (str): Path to the Sphinx project root.
        output_path (str): Folder where output files will be stored.

    Returns:
        bool: True if the process succeeded, False otherwise.
    """
    # Search for the sphinx source folder in multiple possible locations
    possible_sources = [
        os.path.join(input_path, "docs", "source"),  # docs/source
        os.path.join(input_path, "docs"),            # docs
        os.path.join(input_path, "doc", "source"),   # doc/source
        os.path.join(input_path, "doc")              # doc
    ]
    sphinx_source = None
    for candidate in possible_sources:
        conf_py = os.path.join(candidate, "conf.py")
        index_rst = os.path.join(candidate, "index.rst")
        if os.path.exists(conf_py) and os.path.exists(index_rst):
            sphinx_source = candidate
            logger.info(f" 📚 Found sphinx source folder: {sphinx_source}")
            break
    if sphinx_source is None:
        logger.error(" ❌ No valid sphinx source folder found (conf.py and index.rst in docs/source, docs, doc/source, or doc/)")
        return False

    markdown_output = os.path.join(output_path, "output.md")
    notebook_path = os.path.join(input_path, "notebook.ipynb")  # Optional

    # Get absolute path to markdown_builder.py before changing directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    markdown_builder_path = os.path.join(current_dir, "markdown_builder.py")
    logger.info(f" 📚 markdown_builder_path: {markdown_builder_path}")

    # Change to output_path directory to create build artifacts there
    original_cwd = os.getcwd()
    os.chdir(output_path)

    # Extract library name from input path
    library_name = os.path.basename(input_path)

    command = [
        sys.executable, markdown_builder_path,
        "--sphinx-source", sphinx_source,
        "--output", markdown_output,
        "--source-root", input_path
    ]

    if os.path.exists(notebook_path):
        command += ["--notebook", notebook_path]

    logger.info(f" 📚 Executing: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.stdout:
            logger.info(f"markdown_builder.py STDOUT:\n{result.stdout}")
        if result.stderr.strip():
            logger.error(f"markdown_builder.py STDERR:\n{result.stderr}")
        
        if result.returncode != 0:
            logger.warning(f"markdown_builder.py returned non-zero exit code: {result.returncode}")
            logger.warning("Continuing anyway as some markdown files might have been generated")
            
    except Exception as e:
        logger.error(" ❌ markdown_builder.py failed with exception.")
        logger.error(f"Exception: {e}")
        return False
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
    # Markdown to txt
    if os.path.exists(markdown_output):
        txt_output_path = auxiliary.convert_markdown_to_txt(output_path, library_name)
        logger.info(f" ✅ Markdown converted to text at: {txt_output_path}")
        
        # Delete the markdown file after successful conversion
        os.remove(markdown_output)
        logger.info(f" 📄 Deleted temporary markdown file: {markdown_output}")
        
        return True
    else:
        logger.warning(f"Markdown file not found at expected path: {output_path}")
        return False