"""
Text conversion utilities for converters.
Handles Markdown to text conversion.
"""

import os
import logging
import html2text

logger = logging.getLogger(__name__)


def convert_markdown_to_txt(output_folder: str, library_name: str) -> str:
    """
    Convert the output.md file in the output folder to a .txt file with library name.

    Args:
        output_folder (str): Folder containing output.md file.
        library_name (str): Name of the library for the txt filename.

    Returns:
        str: Path to the created .txt file.
    """
    md_path = os.path.join(output_folder, "output.md")
    if not os.path.isfile(md_path):
        logger.error(f"Markdown file does not exist: {md_path}")
        raise FileNotFoundError(md_path)

    with open(md_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    txt_filename = f"{library_name}.txt"
    txt_path = os.path.join(output_folder, txt_filename)

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(content)

    logger.info(f"✅ Markdown converted to text at: {txt_path}")
    return txt_path


def markdown_to_text(md_file_path: str, txt_file_path: str):
    """
    Convert a Markdown (.md) file to plain text (.txt) using markdown and html2text.
    
    Args:
        md_file_path (str): Path to the input Markdown file.
        txt_file_path (str): Path to the output text file.
    """
    try:
        # Read the markdown file
        with open(md_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML first
        try:
            import markdown
            html_content = markdown.markdown(markdown_content)
        except ImportError:
            logger.warning("markdown library not available, using raw content")
            html_content = f"<pre>{markdown_content}</pre>"
        
        # Convert HTML to plain text
        try:
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0  # No line wrapping
            text_content = h.handle(html_content)
        except Exception as e:
            logger.warning(f"html2text conversion failed: {e}, using raw content")
            text_content = markdown_content
        
        # Write the text file
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        logger.info(f"✅ Markdown converted to text: {txt_file_path}")
        
    except Exception as e:
        logger.error(f"❌ Failed to convert markdown to text: {e}")
        # Fallback: copy content as-is
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fallback: content copied as-is to: {txt_file_path}")
        except Exception as fallback_e:
            logger.error(f"❌ Fallback also failed: {fallback_e}")
            raise
