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
try:
    from .converters import nonsphinx_converter, auxiliary
    from .dependency_manager import dependency_manager
    from .build_manager import build_manager
except ImportError:
    from converters import nonsphinx_converter, auxiliary
    from dependency_manager import dependency_manager
    from build_manager import build_manager
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
    parser.add_argument('--rough', '-r', action='store_true', help='Save directly to specified output file without creating folders')
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
    """
    Try to ensure the library is installed, but continue processing even if it fails.
    This allows processing of repositories that contain only notebooks or documentation
    without an installable Python package.
    
    Returns:
        bool: True if library is available, False otherwise
    """
    # Use the enhanced dependency manager
    from .dependency_manager import dependency_manager
    return dependency_manager.ensure_library_installed(library_name)


def main():
    try:
        args = parse_args()
        
        # Appelle la fonction make() avec les arguments parsés
        result = make(
            library_name=args.library_name,
            output_path=args.output,
            input_path=args.input_path,
            extension=args.extension,
            rough=args.rough
        )
        
        if result:
            logger.info(f"✅ Conversion completed successfully. Output: {result}")
        else:
            logger.error("❌ Conversion failed")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        sys.exit(1)


def make(library_name, output_path=None, input_path=None, extension='txt', rough=False):
    """
    Convert a library's documentation to text or markdown format (programmatic API).
    Args:
        library_name (str): Name of the library to convert (e.g., "pixell", "numpy").
        output_path (str, optional): Output directory or file path. Defaults to ~/your_context_library/.
        input_path (str, optional): Manual path to library (overrides automatic search).
        extension (str, optional): Output file extension: 'txt' (default) or 'md'.
        rough (bool, optional): If True and output_path is a file path, save directly to that file without creating folders.
    Returns:
        str: Path to the generated documentation file, or None if failed.
    """
    try:
        # Set up build environment with dependency management
        logger.info("🔧 Setting up build environment...")
        if not build_manager.ensure_build_environment():
            logger.warning("⚠️ Build environment setup had issues, continuing anyway...")
        
        # Try to ensure target library is installed, but continue even if it fails
        library_available = ensure_library_installed(library_name)
        if not library_available:
            logger.info(f" Processing documentation for '{library_name}' without the library being installed.")
        
        # Determine input path
        if input_path:
            input_path = os.path.abspath(input_path)
            logger.info(f" Using manual path: {input_path}")
        else:
            logger.info(f"🔍 Searching for library '{library_name}'...")
            input_path = auxiliary.find_library_path(library_name)
            if not input_path:
                logger.error(f"❌ Library '{library_name}' not found. Try specifying the path manually with input_path.")
                return None
        
        # Ensure CAMB is built if processing CAMB (only if library is available)
        if library_name.lower() == "camb" and library_available:
            auxiliary.ensure_camb_built(input_path)
            auxiliary.patch_camb_sys_exit(input_path)

        # Determine output path
        if output_path:
            output_path = os.path.abspath(output_path)
            # Check if output_path is a file path (has extension) and rough mode is enabled
            if rough and os.path.splitext(output_path)[1]:
                # Rough mode: output_path is a file path, extract directory
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                logger.info(f" Rough mode enabled: will save directly to {output_path}")
            else:
                # Normal mode: output_path is a directory
                if not os.path.splitext(output_path)[1]:  # No extension, treat as directory
                    os.makedirs(output_path, exist_ok=True)
        else:
            output_path = auxiliary.get_default_output_path()
            os.makedirs(output_path, exist_ok=True)

        logger.info(f" Input path: {input_path}")
        logger.info(f" Output path: {output_path}")

        if not os.path.exists(input_path):
            logger.error(f"Input path '{input_path}' does not exist.")
            return None

        if not os.listdir(input_path):
            logger.error(f"Input path '{input_path}' is empty.")
            return None

        doc_format = auxiliary.find_format(input_path)
        logger.info(f"  Detected documentation format: {doc_format}")

        # Ensure Sphinx extensions are installed if this is a Sphinx project
        if doc_format == 'sphinx_makefile':
            logger.info("🔍 Ensuring Sphinx extensions are installed...")
            dependency_manager.ensure_sphinx_extensions(input_path)

        output_file = None
        success = False

        # Try Sphinx conversion first
        if doc_format == 'sphinx_makefile':
            output_file, success = _try_sphinx_conversion(
                input_path, output_path, library_name, extension, rough
            )

        # If Sphinx failed, try non-Sphinx fallback
        if not success:
            output_file, success = _try_nonsphinx_fallback(
                input_path, output_path, library_name, extension, rough
            )

        # If still no success, try notebook fallback
        if not success:
            output_file, success = _try_notebook_fallback(
                input_path, output_path, library_name, extension, rough
            )

        # Final result handling
        if success and output_file:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file}")
            
            # Convert to text if needed
            if extension == 'txt' and not output_file.endswith('.txt'):
                final_output = _convert_to_text(output_file)
            else:
                final_output = output_file
            
            if not library_available:
                logger.info(f" Documentation processed successfully despite library '{library_name}' not being available as a Python package.")
            
            return final_output
        else:
            logger.error("❌ All conversion methods failed: Sphinx, non-Sphinx, and notebooks")
            return None

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        raise


def _try_sphinx_conversion(input_path, output_path, library_name, extension, rough):
    """Try Sphinx conversion methods."""
    logger.info("🔍 Attempting Sphinx documentation build...")
    
    # Try Makefile first
    makefile_dir = auxiliary.find_sphinx_makefile(input_path)
    if makefile_dir:
        logger.info(f"📋 Using Sphinx Makefile from: {makefile_dir}")
        
        from contextmaker.converters.markdown_builder import build_via_makefile, combine_text_files, find_notebooks_in_doc_dirs, convert_notebook
        
        # Try Makefile first
        build_dir = build_via_makefile(makefile_dir, input_path, 'text')
        
        if not build_dir:
            # Makefile failed, try direct Sphinx building as fallback
            logger.info("📋 Makefile build failed, trying direct Sphinx building...")
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                from contextmaker.converters.markdown_builder import build_sphinx_directly
                build_dir = build_sphinx_directly(sphinx_source, 'text')
                if build_dir:
                    logger.info("✅ Direct Sphinx build successful as fallback!")
                else:
                    logger.error("❌ Both Makefile and direct Sphinx building failed")
                    return None, False
            else:
                logger.error("❌ Could not find Sphinx source directory for fallback")
                return None, False
        
        if build_dir:
            # Create output file path
            if extension == 'txt':
                if rough and os.path.splitext(output_path)[1]:
                    output_file = output_path
                else:
                    output_file = os.path.join(output_path, f"{library_name}.txt")
                
                # Combine text files directly
                success = combine_text_files(build_dir, output_file, library_name)
                
                # Add notebooks if found
                if success:
                    _add_notebooks_to_file(input_path, output_file)
                
                return output_file, success
            else:
                # For markdown output, convert text to markdown
                temp_txt = os.path.join(output_path, f"{library_name}_temp.txt")
                success = combine_text_files(build_dir, temp_txt, library_name)
                
                if success:
                    _add_notebooks_to_file(input_path, temp_txt)
                    
                    # Convert to markdown
                    if rough and os.path.splitext(output_path)[1]:
                        output_file = output_path
                    else:
                        output_file = os.path.join(output_path, f"{library_name}.md")
                    
                    from contextmaker.converters.markdown_builder import markdown_to_text
                    markdown_to_text(temp_txt, output_file)
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_txt)
                    except Exception:
                        pass
                    
                    return output_file, True
    
    # Try standard Sphinx method
    sphinx_source = auxiliary.find_sphinx_source(input_path)
    if sphinx_source:
        from contextmaker.converters.markdown_builder import build_markdown, combine_markdown, find_notebooks_in_doc_dirs, convert_notebook, append_notebook_markdown
        
        conf_path = os.path.join(sphinx_source, "conf.py")
        index_path = os.path.join(sphinx_source, "index.rst")
        
        if rough and os.path.splitext(output_path)[1]:
            output_file = output_path
        else:
            output_file = os.path.join(output_path, f"{library_name}.md")
        
        logger.info(f"📚 Building Sphinx documentation from: {sphinx_source}")
        build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=False)
        
        import glob
        md_files = glob.glob(os.path.join(build_dir, "*.md"))
        if not md_files:
            logger.warning("📚 Sphinx build with original conf.py failed. Trying with minimal configuration...")
            build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=True)
            md_files = glob.glob(os.path.join(build_dir, "*.md"))
        
        if md_files:
            logger.info(f"✅ Sphinx build successful! Generated {len(md_files)} markdown files")
            combine_markdown(build_dir, [], output_file, index_path, library_name)
            
            # Add notebooks
            for nb_path in find_notebooks_in_doc_dirs(input_path):
                notebook_md = convert_notebook(nb_path)
                if notebook_md:
                    append_notebook_markdown(output_file, notebook_md)
            
            return output_file, True
        else:
            logger.warning("📚 Sphinx build failed even with minimal configuration")
    
    return None, False


def _try_nonsphinx_fallback(input_path, output_path, library_name, extension, rough):
    """Try non-Sphinx converter as fallback."""
    logger.info("🔄 Trying non-Sphinx converter...")
    
    from contextmaker.converters import nonsphinx_converter
    
    try:
        if rough and os.path.splitext(output_path)[1]:
            # Rough mode: create in temp directory first, then copy to desired location
            temp_output_dir = os.path.dirname(output_path)
            success = nonsphinx_converter.create_final_markdown(input_path, temp_output_dir, library_name)
            if success:
                # Copy the generated file to the desired location
                temp_file = os.path.join(temp_output_dir, f"{library_name}.txt")
                if os.path.exists(temp_file):
                    import shutil
                    shutil.copy2(temp_file, output_path)
                    output_file = output_path
                    # Clean up temp file
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass
                    return output_file, True
        else:
            # Normal mode: create filename in output directory
            success = nonsphinx_converter.create_final_markdown(input_path, output_path, library_name)
            if success:
                output_file = os.path.join(output_path, f"{library_name}.md")
                return output_file, True
                
    except Exception as e:
        logger.warning(f"⚠️ Non-Sphinx converter failed: {e}")
    
    return None, False


def _try_notebook_fallback(input_path, output_path, library_name, extension, rough):
    """Try notebook extraction as last resort."""
    logger.info("🔄 Trying notebooks as last resort...")
    
    from contextmaker.converters.markdown_builder import find_notebooks_in_doc_dirs
    
    notebooks_found = find_notebooks_in_doc_dirs(input_path)
    
    if notebooks_found:
        logger.info(f"🚀 Found {len(notebooks_found)} notebooks! Creating documentation from notebooks...")
        
        # Create output file directly from notebooks
        if rough and os.path.splitext(output_path)[1]:
            output_file = output_path
        else:
            output_file = os.path.join(output_path, f"{library_name}.md")
        
        # Create markdown content from notebooks
        notebook_content = []
        notebook_content.append(f"# Documentation for {library_name}\n\n")
        notebook_content.append("## Notebooks\n\n")
        
        for nb_path in notebooks_found:
            notebook_content.append(f"### {os.path.basename(nb_path)}\n\n")
            try:
                # Try to read notebook content
                import nbformat
                nb = nbformat.read(nb_path, as_version=4)
                
                # Extract markdown cells
                for cell in nb.cells:
                    if cell.cell_type == 'markdown':
                        notebook_content.append(cell.source + "\n\n")
                    elif cell.cell_type == 'code':
                        notebook_content.append(f"```python\n{cell.source}\n```\n\n")
            except Exception as e:
                notebook_content.append(f"*[Notebook content could not be read: {e}]*\n\n")
            
            notebook_content.append("---\n\n")
        
        # Write the markdown file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(''.join(notebook_content))
            
            logger.info(f"✅ Documentation created directly from notebooks: {output_file}")
            return output_file, True
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create documentation from notebooks: {e}")
    
    return None, False


def _add_notebooks_to_file(input_path, output_file):
    """Add notebook content to an existing file."""
    from contextmaker.converters.markdown_builder import find_notebooks_in_doc_dirs, convert_notebook
    
    notebooks_found = find_notebooks_in_doc_dirs(input_path)
    if notebooks_found:
        logger.info(f"📒 Found {len(notebooks_found)} notebooks, appending to documentation...")
        
        # Read the current content
        with open(output_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Append notebooks
        notebook_content = []
        for nb_path in notebooks_found:
            notebook_md = convert_notebook(nb_path)
            if notebook_md:
                notebook_content.append(f"\n## Notebook: {os.path.basename(nb_path)}\n")
                try:
                    with open(notebook_md, 'r', encoding='utf-8') as f:
                        notebook_md_content = f.read()
                    notebook_content.append(notebook_md_content)
                except Exception as e:
                    logger.warning(f"⚠️ Could not read notebook markdown {notebook_md}: {e}")
                    notebook_content.append(f"[Notebook content could not be read: {notebook_md}]")
                notebook_content.append("\n" + "-" * 50 + "\n")
        
        if notebook_content:
            # Write back with notebooks
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(current_content + ''.join(notebook_content))
            logger.info(f"✅ Added {len(notebooks_found)} notebooks to documentation")


def _convert_to_text(markdown_file):
    """Convert markdown file to text and clean up."""
    from contextmaker.converters.markdown_builder import markdown_to_text
    
    txt_file = os.path.splitext(markdown_file)[0] + ".txt"
    markdown_to_text(markdown_file, txt_file)
    
    if os.path.exists(txt_file):
        try:
            os.remove(markdown_file)
            logger.info(f"Deleted markdown file after text conversion: {markdown_file}")
        except Exception as e:
            logger.warning(f"Could not delete markdown file: {markdown_file}. Error: {e}")
        return txt_file
    
    return markdown_file


if __name__ == "__main__":
    main()