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
from contextmaker.dependency_manager import dependency_manager
from contextmaker.build_manager import build_manager
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
        
        # Set up build environment with dependency management
        logger.info("🔧 Setting up build environment...")
        if not build_manager.ensure_build_environment():
            logger.warning("⚠️ Build environment setup had issues, continuing anyway...")
        
        # Try to ensure target library is installed, but continue even if it fails
        library_available = ensure_library_installed(args.library_name)
        if not library_available:
            logger.info(f" Processing documentation for '{args.library_name}' without the library being installed.")
        
        # Determine input path
        if args.input_path:
            # Manual path provided
            input_path = os.path.abspath(args.input_path)
            logger.info(f" Using manual path: {input_path}")
        else:
            # Automatic search
            logger.info(f"🔍 Searching for library '{args.library_name}'...")
            input_path = auxiliary.find_library_path(args.library_name)
            if not input_path:
                logger.error(f"❌ Library '{args.library_name}' not found. Try specifying the path manually with --input_path")
                sys.exit(1)
        
        # Ensure CAMB is built if processing CAMB (only if library is available)
        if args.library_name.lower() == "camb" and library_available:
            auxiliary.ensure_camb_built(input_path)
            auxiliary.patch_camb_sys_exit(input_path)
        
        # Determine output path
        if args.output:
            output_path = os.path.abspath(args.output)
        else:
            output_path = auxiliary.get_default_output_path()
        
        logger.info(f" Input path: {input_path}")
        logger.info(f" Output path: {output_path}")

        if not os.path.exists(input_path):
            logger.error(f"Input path '{input_path}' does not exist.")
            sys.exit(1)

        if not os.listdir(input_path):
            logger.error(f"Input path '{input_path}' is empty.")
            sys.exit(1)

        # Handle rough mode for main function
        if args.rough and args.output and os.path.splitext(output_path)[1]:
            # Rough mode: output_path is a file path, extract directory
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            logger.info(f" Rough mode enabled: will save directly to {output_path}")
        else:
            # Normal mode: output_path is a directory
            if not args.output or not os.path.splitext(output_path)[1]:  # No extension, treat as directory
                os.makedirs(output_path, exist_ok=True)

        doc_format = auxiliary.find_format(input_path)
        logger.info(f"  Detected documentation format: {doc_format}")

        # Ensure Sphinx extensions are installed if this is a Sphinx project
        if doc_format == 'sphinx_makefile':
            logger.info("🔍 Ensuring Sphinx extensions are installed...")
            dependency_manager.ensure_sphinx_extensions(input_path)

        extension = args.extension
        output_file = None

        if doc_format == 'sphinx_makefile':
            # Highest priority: Use Sphinx Makefile
            from contextmaker.converters.markdown_builder import build_via_makefile, build_sphinx_directly, combine_text_files, find_notebooks_in_doc_dirs, convert_notebook
            makefile_dir = auxiliary.find_sphinx_makefile(input_path)
            if makefile_dir:
                logger.info(f"📋 Using Sphinx Makefile from: {makefile_dir}")
                
                # Try Makefile first
                build_dir = build_via_makefile(makefile_dir, input_path, 'text')
                
                if not build_dir:
                    # Makefile failed, try direct Sphinx building as fallback
                    logger.info("📋 Makefile build failed, trying direct Sphinx building...")
                    sphinx_source = auxiliary.find_sphinx_source(input_path)
                    if sphinx_source:
                        build_dir = build_sphinx_directly(sphinx_source, 'text')
                        if build_dir:
                            logger.info("✅ Direct Sphinx build successful as fallback!")
                        else:
                            logger.error("❌ Both Makefile and direct Sphinx building failed")
                            success = False
                    else:
                        logger.error("❌ Could not find Sphinx source directory for fallback")
                        success = False
                
                if build_dir:
                    # Create output file path
                    if extension == 'txt':
                        if args.rough and args.output and os.path.splitext(output_path)[1]:
                            # Rough mode: use output_path directly as it's already a file path
                            output_file = output_path
                        else:
                            # Normal mode: create filename in output directory
                            output_file = os.path.join(output_path, f"{args.library_name}.txt")
                        # Combine text files directly
                        success = combine_text_files(build_dir, output_file, args.library_name)
                        
                        # Add notebooks to the text file if any are found
                        if success:
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
                                        # Read the content of the markdown file, not just the path
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
                    else:
                        # For markdown output, we'll need to convert text to markdown
                        temp_txt = os.path.join(output_path, f"{args.library_name}_temp.txt")
                        success = combine_text_files(build_dir, temp_txt, args.library_name)
                        
                        # Add notebooks to the temp text file if any are found
                        if success:
                            notebooks_found = find_notebooks_in_doc_dirs(input_path)
                            if notebooks_found:
                                logger.info(f"📒 Found {len(notebooks_found)} notebooks, appending to documentation...")
                                # Read the current content
                                with open(temp_txt, 'r', encoding='utf-8') as f:
                                    current_content = f.read()
                                
                                # Append notebooks
                                notebook_content = []
                                for nb_path in notebooks_found:
                                    notebook_md = convert_notebook(nb_path)
                                    if notebook_md:
                                        notebook_content.append(f"\n## Notebook: {os.path.basename(nb_path)}\n")
                                        # Read the content of the markdown file, not just the path
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
                                    with open(temp_txt, 'w', encoding='utf-8') as f:
                                        f.write(current_content + ''.join(notebook_content))
                                    logger.info(f"✅ Added {len(notebooks_found)} notebooks to documentation")
                            
                            # Convert to markdown
                            if args.rough and args.output and os.path.splitext(output_path)[1]:
                                # Rough mode: use output_path directly as it's already a file path
                                output_file = output_path
                            else:
                                # Normal mode: create filename in output directory
                                output_file = os.path.join(output_path, f"{args.library_name}.md")
                            markdown_to_text(temp_txt, output_file)
                            # Clean up temp file
                            try:
                                os.remove(temp_txt)
                            except Exception:
                                pass
                else:
                    logger.warning("⚠️ All Sphinx build methods failed, will try standard Sphinx method next")
                    success = False
            else:
                logger.warning("⚠️ Makefile directory not found, will try standard Sphinx method next")
                success = False

        # Always try Sphinx methods before falling back to non-Sphinx
        if not output_file and not success:
            # Try standard Sphinx method (either as primary method or as fallback)
            logger.info("🔍 Attempting standard Sphinx documentation build...")
            from contextmaker.converters.markdown_builder import build_markdown, combine_markdown, find_notebooks_in_doc_dirs, convert_notebook, append_notebook_markdown
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                conf_path = os.path.join(sphinx_source, "conf.py")
                index_path = os.path.join(sphinx_source, "index.rst")
                if args.rough and args.output and os.path.splitext(output_path)[1]:
                    # Rough mode: use output_path directly as it's already a file path
                    output_file = output_path
                else:
                    # Normal mode: create filename in output directory
                    output_file = os.path.join(output_path, f"{args.library_name}.md")
                
                logger.info(f"📚 Building Sphinx documentation from: {sphinx_source}")
                build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=False)
                import glob
                md_files = glob.glob(os.path.join(build_dir, "*.md"))
                if not md_files:
                    logger.warning("📚 Sphinx build with original conf.py failed or produced no markdown. Trying with minimal configuration...")
                    build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=True)
                    md_files = glob.glob(os.path.join(build_dir, "*.md"))
                
                if md_files:
                    logger.info(f"✅ Sphinx build successful! Generated {len(md_files)} markdown files")
                    combine_markdown(build_dir, [], output_file, index_path, args.library_name)
                    appended_notebooks = set()
                    for nb_path in find_notebooks_in_doc_dirs(input_path):
                        notebook_md = convert_notebook(nb_path)
                        if notebook_md:
                            append_notebook_markdown(output_file, notebook_md)
                            appended_notebooks.add(os.path.abspath(nb_path))
                    success = True
                else:
                    logger.warning("📚 Sphinx build failed even with minimal configuration")
                    success = False
            else:
                logger.info("📚 No Sphinx source directory found")
                success = False

        # Only if all Sphinx methods failed, try non-Sphinx converter as last resort
        if not output_file and not success:
            logger.info("🔄 All Sphinx methods failed, falling back to non-Sphinx converter as last resort...")
            # For non-Sphinx projects, we need to handle rough mode differently
            if args.rough and args.output and os.path.splitext(output_path)[1]:
                # Rough mode: create in temp directory first, then copy to desired location
                temp_output_dir = os.path.dirname(output_path)
                success = nonsphinx_converter.create_final_markdown(input_path, temp_output_dir, args.library_name)
                if success:
                    # Copy the generated file to the desired location
                    temp_file = os.path.join(temp_output_dir, f"{args.library_name}.txt")
                    if os.path.exists(temp_file):
                        import shutil
                        shutil.copy2(temp_file, output_path)
                        output_file = output_path
                        # Clean up temp file
                        try:
                            os.remove(temp_file)
                        except Exception:
                            pass
                    else:
                        success = False
            else:
                # Normal mode: create filename in output directory
                success = nonsphinx_converter.create_final_markdown(input_path, output_path, args.library_name)
                output_file = os.path.join(output_path, f"{args.library_name}.md")
        
        if success and output_file:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file}")
            if extension == 'txt':
                # Check if the output file is already a text file (from Makefile)
                if output_file.endswith('.txt'):
                    final_output = output_file
                else:
                    # Convert markdown to text
                    txt_file = os.path.splitext(output_file)[0] + ".txt"
                    markdown_to_text(output_file, txt_file)
                    # Delete the markdown file after successful text conversion
                    if os.path.exists(txt_file):
                        try:
                            os.remove(output_file)
                            logger.info(f"Deleted markdown file after text conversion: {output_file}")
                        except Exception as e:
                            logger.warning(f"Could not delete markdown file: {output_file}. Error: {e}")
                    final_output = txt_file
            else:
                final_output = output_file
            
            if not library_available:
                logger.info(f" Documentation processed successfully despite library '{args.library_name}' not being available as a Python package.")
            
            return final_output
        else:
            logger.warning("  Conversion completed with warnings or partial results.")

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

        if doc_format == 'sphinx_makefile':
            # Highest priority: Use Sphinx Makefile
            from contextmaker.converters.markdown_builder import build_via_makefile, build_sphinx_directly, combine_text_files, find_notebooks_in_doc_dirs, convert_notebook
            makefile_dir = auxiliary.find_sphinx_makefile(input_path)
            if makefile_dir:
                logger.info(f"📋 Using Sphinx Makefile from: {makefile_dir}")
                
                # Try Makefile first
                build_dir = build_via_makefile(makefile_dir, input_path, 'text')
                
                if not build_dir:
                    # Makefile failed, try direct Sphinx building as fallback
                    logger.info("📋 Makefile build failed, trying direct Sphinx building...")
                    sphinx_source = auxiliary.find_sphinx_source(input_path)
                    if sphinx_source:
                        build_dir = build_sphinx_directly(sphinx_source, 'text')
                        if build_dir:
                            logger.info("✅ Direct Sphinx build successful as fallback!")
                        else:
                            logger.error("❌ Both Makefile and direct Sphinx building failed")
                            success = False
                    else:
                        logger.error("❌ Could not find Sphinx source directory for fallback")
                        success = False
                
                if build_dir:
                    # Create output file path
                    if extension == 'txt':
                        if rough and os.path.splitext(output_path)[1]:
                            # Rough mode: use output_path directly as it's already a file path
                            output_file = output_path
                        else:
                            # Normal mode: create filename in output directory
                            output_file = os.path.join(output_path, f"{library_name}.txt")
                        # Combine text files directly
                        success = combine_text_files(build_dir, output_file, library_name)
                        
                        # Add notebooks to the text file if any are found
                        if success:
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
                                        # Read the content of the markdown file, not just the path
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
                    else:
                        # For markdown output, we'll need to convert text to markdown
                        temp_txt = os.path.join(output_path, f"{library_name}_temp.txt")
                        success = combine_text_files(build_dir, temp_txt, library_name)
                        
                        # Add notebooks to the temp text file if any are found
                        if success:
                            notebooks_found = find_notebooks_in_doc_dirs(input_path)
                            if notebooks_found:
                                logger.info(f"📒 Found {len(notebooks_found)} notebooks, appending to documentation...")
                                # Read the current content
                                with open(temp_txt, 'r', encoding='utf-8') as f:
                                    current_content = f.read()
                                
                                # Append notebooks
                                notebook_content = []
                                for nb_path in notebooks_found:
                                    notebook_md = convert_notebook(nb_path)
                                    if notebook_md:
                                        notebook_content.append(f"\n## Notebook: {os.path.basename(nb_path)}\n")
                                        # Read the content of the markdown file, not just the path
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
                                    with open(temp_txt, 'w', encoding='utf-8') as f:
                                        f.write(current_content + ''.join(notebook_content))
                                    logger.info(f"✅ Added {len(notebooks_found)} notebooks to documentation")
                            
                            # Convert to markdown
                            if rough and os.path.splitext(output_path)[1]:
                                # Rough mode: use output_path directly as it's already a file path
                                output_file = output_path
                            else:
                                # Normal mode: create filename in output directory
                                output_file = os.path.join(output_path, f"{library_name}.md")
                            markdown_to_text(temp_txt, output_file)
                            # Clean up temp file
                            try:
                                os.remove(temp_txt)
                            except Exception:
                                pass
                else:
                    logger.warning("⚠️ All Sphinx build methods failed, will try standard Sphinx method next")
                    success = False
            else:
                logger.warning("⚠️ Makefile directory not found, will try standard Sphinx method next")
                success = False

        # Always try Sphinx methods before falling back to non-Sphinx
        if not output_file and not success:
            # Try standard Sphinx method (either as primary method or as fallback)
            logger.info("🔍 Attempting standard Sphinx documentation build...")
            from contextmaker.converters.markdown_builder import build_markdown, combine_markdown, find_notebooks_in_doc_dirs, convert_notebook, append_notebook_markdown
            sphinx_source = auxiliary.find_sphinx_source(input_path)
            if sphinx_source:
                conf_path = os.path.join(sphinx_source, "conf.py")
                index_path = os.path.join(sphinx_source, "index.rst")
                if rough and os.path.splitext(output_path)[1]:
                    # Rough mode: use output_path directly as it's already a file path
                    output_file = output_path
                else:
                    # Normal mode: create filename in output directory
                    output_file = os.path.join(output_path, f"{library_name}.md")
                
                logger.info(f"📚 Building Sphinx documentation from: {sphinx_source}")
                build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=False)
                import glob
                md_files = glob.glob(os.path.join(build_dir, "*.md"))
                if not md_files:
                    logger.warning("📚 Sphinx build with original conf.py failed or produced no markdown. Trying with minimal configuration...")
                    build_dir = build_markdown(sphinx_source, conf_path, input_path, robust=True)
                    md_files = glob.glob(os.path.join(build_dir, "*.md"))
                
                if md_files:
                    logger.info(f"✅ Sphinx build successful! Generated {len(md_files)} markdown files")
                    combine_markdown(build_dir, [], output_file, index_path, library_name)
                    appended_notebooks = set()
                    for nb_path in find_notebooks_in_doc_dirs(input_path):
                        notebook_md = convert_notebook(nb_path)
                        if notebook_md:
                            append_notebook_markdown(output_file, notebook_md)
                            appended_notebooks.add(os.path.abspath(nb_path))
                    success = True
                else:
                    logger.warning("📚 Sphinx build failed even with minimal configuration")
                    success = False
            else:
                logger.info("📚 No Sphinx source directory found")
                success = False

        # Only if all Sphinx methods failed, try non-Sphinx converter as last resort
        if not output_file and not success:
            # For non-Sphinx projects, we need to handle rough mode differently
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
                    else:
                        success = False
            else:
                # Normal mode: create filename in output directory
                success = nonsphinx_converter.create_final_markdown(input_path, output_path, library_name)
                output_file = os.path.join(output_path, f"{library_name}.md")

        if success and output_file:
            logger.info(f" ✅ Conversion completed successfully. Output: {output_file}")
            if extension == 'txt':
                # Check if the output file is already a text file (from Makefile)
                if output_file.endswith('.txt'):
                    final_output = output_file
                else:
                    # Convert markdown to text
                    txt_file = os.path.splitext(output_file)[0] + ".txt"
                    markdown_to_text(output_file, txt_file)
                    # Delete the markdown file after successful text conversion
                    if os.path.exists(txt_file):
                        try:
                            os.remove(output_file)
                            logger.info(f"Deleted markdown file after text conversion: {output_file}")
                        except Exception as e:
                            logger.warning(f"Could not delete markdown file: {output_file}. Error: {e}")
                    final_output = txt_file
            else:
                final_output = output_file
            
            if not library_available:
                logger.info(f" Documentation processed successfully despite library '{library_name}' not being available as a Python package.")
            
            return final_output
        else:
            logger.warning("  Conversion completed with warnings or partial results.")
            return None

    except Exception as e:
        logger.exception(f" ❌ An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    main()