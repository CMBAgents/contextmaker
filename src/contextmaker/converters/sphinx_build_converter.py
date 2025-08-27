"""
Sphinx Build Converter
Handles Sphinx documentation conversion without Makefile (fallback Sphinx method).
"""

import os
import logging
import tempfile
import shutil
import subprocess
import glob
from .utils import detector

logger = logging.getLogger(__name__)


class SphinxBuildConverter:
    """Converter for Sphinx documentation without Makefile."""
    
    def convert(self, input_path: str, output_path: str, library_name: str) -> tuple[str | None, bool]:
        """
        Convert Sphinx documentation using direct sphinx-build (without Makefile).
        
        Args:
            input_path: Path to the Sphinx project root
            output_path: Folder where output files will be stored
            library_name: Name of the library
            
        Returns:
            Tuple of (output_file_path, success)
        """
        logger.info("Converting Sphinx documentation using direct build...")
        
        try:
            # Find Sphinx source directory
            sphinx_source = detector.find_sphinx_source(input_path)
            if not sphinx_source:
                logger.warning("No Sphinx source directory found")
                return None, False
            
            # Build Sphinx documentation directly
            build_dir = self._build_sphinx_directly(sphinx_source)
            if not build_dir:
                logger.warning("Sphinx build failed")
                return None, False
            
            # Convert the built documentation to markdown
            markdown_output = os.path.join(output_path, f"{library_name}.md")
            success = self._combine_markdown_files(build_dir, markdown_output, library_name, sphinx_source)
            
            # Clean up build directory
            try:
                shutil.rmtree(build_dir)
            except Exception as e:
                logger.warning(f"Could not clean up build directory: {e}")
            
            if success and os.path.exists(markdown_output):
                logger.info(f"Sphinx build fallback successful: {markdown_output}")
                return markdown_output, True
            else:
                logger.warning("Failed to create markdown file from Sphinx build")
                return None, False
                
        except Exception as e:
            logger.warning(f"Sphinx build fallback failed: {e}")
            return None, False

    def _build_sphinx_directly(self, source_dir: str) -> str | None:
        """Build Sphinx documentation directly using sphinx-build."""
        logger.info(f"Building Sphinx documentation directly (Python fallback) from: {source_dir}")
        
        # Check if sphinx-build is available
        if not shutil.which("sphinx-build"):
            logger.error("'sphinx-build' command not found on this system.")
            logger.error("Install Sphinx: pip install sphinx")
            return None
        
        try:
            # Create a temporary build directory
            build_dir = tempfile.mkdtemp(prefix="sphinx_build_")
            output_dir = os.path.join(build_dir, "html")
            
            # Create build directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Build command
            cmd = [
                "sphinx-build",
                "-b", "html",
                "-d", os.path.join(build_dir, "doctrees"),
                source_dir,
                output_dir
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Execute sphinx-build
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=source_dir
            )
            
            if result.returncode == 0:
                logger.info(f"Sphinx build successful! Output in: {output_dir}")
                return output_dir
            else:
                logger.error(f"Sphinx build failed with return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"stderr: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error building Sphinx documentation: {e}")
            return None

    def _combine_markdown_files(self, build_dir: str, output_file: str, library_name: str, sphinx_source: str) -> bool:
        """Combine HTML files and convert to markdown."""
        try:
            # Find HTML files in the build directory
            html_files = []
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    if file.endswith('.html'):
                        html_files.append(os.path.join(root, file))
            
            if not html_files:
                logger.warning("No HTML files found in build directory")
                return False
            
            logger.info(f"Found {len(html_files)} HTML files")
            
            # Create output directory
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Combine HTML files into markdown
            with open(output_file, 'w', encoding='utf-8') as out:
                out.write(f"# - {library_name} | Complete Documentation -\n\n")
                out.write("## Sphinx Documentation (Direct Build)\n\n")
                out.write(f"*Generated from: {sphinx_source}*\n\n")
                
                for i, html_file in enumerate(html_files):
                    if i > 0:
                        out.write("\n\n---\n\n")
                    
                    # Get relative path for section title
                    relative_path = os.path.relpath(html_file, build_dir)
                    section = os.path.splitext(os.path.basename(html_file))[0]
                    out.write(f"## {section}\n\n")
                    
                    # Convert HTML to markdown (simplified conversion)
                    try:
                        with open(html_file, 'r', encoding='utf-8') as infile:
                            html_content = infile.read()
                            # Simple HTML to markdown conversion
                            markdown_content = self._html_to_markdown(html_content)
                            out.write(markdown_content)
                    except Exception as e:
                        out.write(f"*[Content could not be read: {e}]*\n")
                    
                    out.write("\n\n")
            
            logger.info(f"Combined markdown written to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to combine markdown files: {e}")
            return False

    def _html_to_markdown(self, html_content: str) -> str:
        """Simple HTML to markdown conversion."""
        try:
            # Try to use html2text if available
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0
            return h.handle(html_content)
        except ImportError:
            # Fallback: basic HTML tag removal
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html_content)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            return text
