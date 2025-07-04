import subprocess
import os
import sys
import logging
from converters import auxiliary

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
    sphinx_source = os.path.join(input_path, "docs", "source")
    markdown_output = os.path.join(output_path, "output.md")
    notebook_path = os.path.join(input_path, "notebook.ipynb")  # Optional

    if not os.path.exists(sphinx_source):
        logger.error(f"Sphinx source folder not found at: {sphinx_source}")
        return False

    command = [
        sys.executable, "converters/markdown_builder.py",
        "--sphinx-source", sphinx_source,
        "--output", markdown_output
    ]

    if os.path.exists(notebook_path):
        command += ["--notebook", notebook_path]

    logger.info(f"Executing: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info("✅ Sphinx to Markdown conversion successful.")
        if result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")
        if result.stderr.strip():
            logger.warning(f"STDERR (warnings):\n{result.stderr}")

    except subprocess.CalledProcessError as e:
        logger.error("❌ markdown_builder.py failed.")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"STDOUT:\n{e.stdout}")
        logger.error(f"STDERR:\n{e.stderr}")
        return False

    # Optional markdown to txt
    if os.path.exists(markdown_output):
        txt_output_path = auxiliary.convert_markdown_to_txt(output_path)
        logger.info(f"✅ Markdown converted to text at: {txt_output_path}")
        return True
    else:
        logger.warning(f"Markdown file not found at expected path: {markdown_output}")
        return False