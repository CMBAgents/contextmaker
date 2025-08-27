"""
Non-Sphinx Converter
Handles non-Sphinx documentation conversion (markdown, docstrings, etc.).
"""

import subprocess
import os
import sys
import ast
import shutil
import logging
from .utils import detector
import html2text

logger = logging.getLogger(__name__)
# Removed logging.basicConfig(level=logging.INFO) to avoid conflicts with main logging configuration


class NonsphinxConverter:
    """Converter for non-Sphinx documentation."""
    
    def convert(self, input_path: str, output_path: str, library_name: str) -> tuple[str | None, bool]:
        """
        Create the final text file from the library documentation or source files.
        
        Args:
            input_path: Path to the library or documentation source
            output_path: Path where the final text file will be saved
            library_name: Name of the library for the output file
            
        Returns:
            Tuple of (output_file_path, success)
        """
        try:
            temp_output_path = self._create_markdown_files(input_path, output_path)
            if library_name is None:
                library_name = os.path.basename(os.path.normpath(input_path))
            
            success = self._combine_markdown_files(temp_output_path, output_path, library_name)
            shutil.rmtree(temp_output_path, ignore_errors=True)
            logger.info(f"Temporary folder '{temp_output_path}' removed after processing.")
            
            if success:
                expected_file = os.path.join(output_path, f"{library_name}.md")
                if os.path.exists(expected_file):
                    logger.info(f"Non-Sphinx conversion successful: {expected_file}")
                    return expected_file, True
                else:
                    logger.warning("Non-Sphinx conversion succeeded but output file not found")
                    return None, False
            else:
                logger.warning("Non-Sphinx conversion failed")
                return None, False
                
        except Exception as e:
            logger.warning(f"Non-Sphinx fallback failed: {e}")
            return None, False

    def _create_markdown_files(self, lib_path, output_path):
        """
        Generate markdown files from the library source files.
        
        Args:
            lib_path: Path to the source library or documentation
            output_path: Path where the temporary markdown files will be saved
            
        Returns:
            Path to the temporary directory containing the markdown files
        """
        temp_output_path = os.path.join(output_path, "temp")
        os.makedirs(temp_output_path, exist_ok=True)

        # Track if we found any valid files
        found_files = False
        
        # Note: Notebooks are now handled centrally by contextmaker.py after conversion
        # This converter focuses only on Python files, docstrings, and basic documentation
        
        # Process Python files
        for root, dirs, files in os.walk(lib_path):
            # Skip common directories that don't contain documentation
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules']]
            
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    if detector.has_docstrings(full_path):
                        self._docstrings_to_markdown(full_path, temp_output_path)
                        found_files = True
                    elif detector.has_source(lib_path):
                        self._source_to_markdown(full_path, temp_output_path)
                        found_files = True
        
        if not found_files:
            logger.warning("No documentation files found in the library. This may be a library without docstrings or documentation.")
            # Create a basic documentation file from README or similar
            self._create_basic_documentation(lib_path, temp_output_path)
        
        return temp_output_path

    def _combine_markdown_files(self, temp_output_path, output_path, library_name):
        """
        Combine all markdown files in the temporary directory into a single markdown file.
        
        Args:
            temp_output_path: Path to temporary directory with markdown files
            output_path: Path where final markdown file will be saved
            library_name: Name of the library for the output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all markdown files
            md_files = []
            for root, dirs, files in os.walk(temp_output_path):
                for file in files:
                    if file.endswith((".md", ".txt")):
                        md_files.append(os.path.join(root, file))
            
            if not md_files:
                logger.warning("No markdown files found to combine")
                return False
            
            # Sort files for consistent output
            md_files.sort()
            
            # Combine all markdown content
            combined_content = []
            combined_content.append(f"# Documentation for {library_name}\n\n")
            
            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            combined_content.append(content)
                            combined_content.append("\n\n---\n\n")
                except Exception as e:
                    logger.warning(f"Could not read markdown file {md_file}: {e}")
            
            # Remove the last separator
            if combined_content and combined_content[-1] == "\n\n---\n\n":
                combined_content.pop()
            
            # Write combined content to markdown file (txt conversion will be handled by contextmaker.py)
            output_file = os.path.join(output_path, f"{library_name}.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(''.join(combined_content))
            
            logger.info(f"Combined {len(md_files)} markdown files into: {output_file}")
            logger.info("Note: File created as .md - conversion to .txt will be handled by contextmaker.py if requested")
            return True
            
        except Exception as e:
            logger.error(f"Failed to combine markdown files: {e}")
            return False

    def _docstrings_to_markdown(self, py_path, output_path):
        """Extract docstrings from Python file and save as markdown."""
        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST to extract docstrings
            tree = ast.parse(source_code)
            
            # Extract module docstring
            module_doc = ast.get_docstring(tree)
            
            # Extract function and class docstrings
            docstrings = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    doc = ast.get_docstring(node)
                    if doc:
                        docstrings.append(f"**{node.name}:** {doc}")
            
            if module_doc or docstrings:
                output_file = os.path.join(output_path, os.path.basename(py_path).replace(".py", ".md"))
                with open(output_file, 'w', encoding='utf-8') as f:
                    if module_doc:
                        f.write(f"# {os.path.basename(py_path)}\n\n")
                        f.write(f"**Module Docstring:** {module_doc}\n\n")
                    
                    if docstrings:
                        f.write("## Docstrings\n\n")
                        for doc in docstrings:
                            f.write(f"{doc}\n\n")
                
                logger.info(f"Extracted docstrings from: {py_path}")
                
        except Exception as e:
            logger.warning(f"Failed to extract docstrings from {py_path}: {e}")

    def _source_to_markdown(self, py_path, output_path):
        """Convert Python source code to markdown."""
        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            output_file = os.path.join(output_path, os.path.basename(py_path).replace(".py", ".md"))
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {os.path.basename(py_path)}\n\n")
                f.write("```python\n")
                f.write(source_code)
                f.write("\n```\n")
            
            logger.info(f"Converted source to markdown: {py_path}")
            
        except Exception as e:
            logger.warning(f"Failed to convert source {py_path}: {e}")

    def _create_basic_documentation(self, lib_path, output_path):
        """Create basic documentation from README or similar files."""
        try:
            doc_files = ['README.md', 'README.rst', 'README.txt', 'CHANGELOG.md', 'CHANGELOG.rst']
            
            for doc_file in doc_files:
                doc_path = os.path.join(lib_path, doc_file)
                if os.path.exists(doc_path):
                    output_file = os.path.join(output_path, "basic_documentation.md")
                    shutil.copy2(doc_path, output_file)
                    logger.info(f"Created basic documentation from: {doc_file}")
                    return
            
            # If no README found, create minimal documentation
            output_file = os.path.join(output_path, "basic_documentation.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Basic Documentation\n\n")
                f.write(f"Library path: {lib_path}\n\n")
                f.write("No README or documentation files found.\n")
            
            logger.info("Created minimal basic documentation")
            
        except Exception as e:
            logger.warning(f"Failed to create basic documentation: {e}")


# Backward compatibility - keep the old function name
def create_final_markdown(input_path, output_path, library_name=None):
    """Backward compatibility function."""
    converter = NonsphinxConverter()
    return converter.convert(input_path, output_path, library_name)