"""
Notebook Converter
Handles documentation creation from Jupyter notebooks only.
"""

import os
import logging

logger = logging.getLogger(__name__)


class NotebookConverter:
    """Converter for Jupyter notebooks only."""
    
    def convert(self, input_path: str, output_path: str, library_name: str) -> tuple[str | None, bool]:
        """
        Create documentation from notebooks only.
        
        Args:
            input_path: Path to the notebooks
            output_path: Folder where output files will be stored
            library_name: Name of the library
            
        Returns:
            Tuple of (output_file_path, success)
        """
        logger.info("Creating documentation from notebooks only...")
        
        from .utils import find_notebooks_in_doc_dirs
        
        notebooks_found = find_notebooks_in_doc_dirs(input_path)
        
        if notebooks_found:
            logger.info(f"Found {len(notebooks_found)} notebooks! Creating documentation from notebooks...")
            
            # Create output file directly from notebooks
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
                
                logger.info(f"Documentation created directly from notebooks: {output_file}")
                return output_file, True
                
            except Exception as e:
                logger.warning(f"Failed to create documentation from notebooks: {e}")
                return None, False
        
        return None, False
