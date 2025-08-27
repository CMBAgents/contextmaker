"""
Raw Source Code Converter
Handles raw source code extraction and conversion to documentation.
"""

import os
import ast
import logging

logger = logging.getLogger(__name__)


class RawSourceCodeConverter:
    """Converter for raw source code extraction."""
    
    def convert(self, input_path: str, output_path: str, library_name: str) -> tuple[str | None, bool]:
        """
        Create documentation from raw source code.
        
        Args:
            input_path: Path to the source code
            output_path: Folder where output files will be stored
            library_name: Name of the library
            
        Returns:
            Tuple of (output_file_path, success)
        """
        logger.info("Creating documentation from raw source code...")
        
        try:
            # Check if we have Python source files
            py_files = []
            for root, dirs, files in os.walk(input_path):
                # Skip common non-relevant directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'build', 'dist', '.pytest_cache', 'node_modules']]
                
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))
            
            if not py_files:
                logger.warning("No Python source files found")
                return None, False
            
            logger.info(f"Found {len(py_files)} Python source files! Creating documentation from source...")
            
            # Create output file directly from source
            output_file = os.path.join(output_path, f"{library_name}.md")
            
            # Create markdown content from source files
            source_content = []
            source_content.append(f"# Source Code Documentation for {library_name}\n\n")
            source_content.append("## Python Source Files\n\n")
            
            for py_path in py_files[:50]:  # Limit to first 50 files to avoid huge output
                relative_path = os.path.relpath(py_path, input_path)
                source_content.append(f"### {relative_path}\n\n")
                
                try:
                    with open(py_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    # Extract docstrings if any
                    try:
                        tree = ast.parse(source_code)
                        module_doc = ast.get_docstring(tree)
                        if module_doc:
                            source_content.append(f"**Module Docstring:**\n{module_doc}\n\n")
                    except:
                        pass
                    
                    # Add source code
                    source_content.append("```python\n")
                    source_content.append(source_code)
                    source_content.append("\n```\n\n")
                    
                except Exception as e:
                    source_content.append(f"*[Source code could not be read: {e}]*\n\n")
                
                source_content.append("---\n\n")
            
            if len(py_files) > 50:
                source_content.append(f"*... and {len(py_files) - 50} more files*\n\n")
            
            # Write the markdown file
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(''.join(source_content))
                
                logger.info(f"Documentation created from raw source code: {output_file}")
                return output_file, True
                
            except Exception as e:
                logger.warning(f"Failed to create documentation from source code: {e}")
                return None, False
                
        except Exception as e:
            logger.warning(f"Raw source code fallback failed: {e}")
            return None, False
