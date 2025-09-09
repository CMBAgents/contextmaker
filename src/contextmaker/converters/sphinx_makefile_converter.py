"""
Sphinx Makefile Converter
Handles Sphinx documentation conversion using Makefile (highest priority method).
"""

import subprocess
import os
import sys
import logging
import tempfile
import shutil
import glob
from .utils import detector

logger = logging.getLogger(__name__)


class SphinxMakefileConverter:
    """Converter for Sphinx documentation using Makefile."""
    
    def convert(self, input_path: str, output_path: str, library_name: str) -> tuple[str | None, bool]:
        """
        Convert Sphinx documentation to markdown using Makefile.
        
        Args:
            input_path: Path to the Sphinx project root
            output_path: Folder where output files will be stored
            library_name: Name of the library
            
        Returns:
            Tuple of (output_file_path, success)
        """
        logger.info("Converting Sphinx documentation using Makefile...")
        
        # Special handling for CAMB: use the integrated markdown_builder
        if library_name.lower() == "camb":
            logger.info("CAMB detected: using integrated markdown_builder...")
            try:
                # Try multiple import strategies
                camb_markdown_builder = None
                try:
                    from .utils.markdown_builder import main as camb_markdown_builder
                except ImportError:
                    try:
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
                        from markdown_builder import main as camb_markdown_builder
                    except ImportError:
                        # Last resort: direct import
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(
                            "markdown_builder",
                            os.path.join(os.path.dirname(__file__), 'utils', 'markdown_builder.py')
                        )
                        if spec and spec.loader:
                            markdown_builder_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(markdown_builder_module)
                            camb_markdown_builder = markdown_builder_module.main
                
                if camb_markdown_builder:
                    output_file = os.path.join(output_path, f"{library_name}.md")
                    
                    # Call the CAMB markdown builder
                    result = camb_markdown_builder(input_path)
                    if result:
                        # Copy the generated file to our output location
                        shutil.copy2(result, output_file)
                        logger.info(f"CAMB documentation generated successfully using markdown_builder: {output_file}")
                        return output_file, True
                    else:
                        logger.warning("CAMB markdown_builder failed, falling back to standard Sphinx method")
                else:
                    logger.warning("Could not import CAMB markdown_builder, falling back to standard Sphinx method")
            except Exception as e:
                logger.warning(f"CAMB markdown_builder failed: {e}, falling back to standard Sphinx method")
        
        # Find Sphinx source directory
        # First try to find it relative to the Makefile directory
        makefile_dir = detector.find_sphinx_makefile(input_path)
        sphinx_source = None
        
        if makefile_dir:
            # If Makefile is in doc/, look for source in doc/source/
            if makefile_dir.endswith('doc'):
                potential_source = os.path.join(makefile_dir, 'source')
                if os.path.exists(os.path.join(potential_source, 'conf.py')) and os.path.exists(os.path.join(potential_source, 'index.rst')):
                    sphinx_source = potential_source
                    logger.info(f"Found Sphinx source directory relative to Makefile: {sphinx_source}")
        
        # Fallback to standard detection if not found
        if not sphinx_source:
            sphinx_source = detector.find_sphinx_source(input_path)
        
        if not sphinx_source:
            logger.error("No valid sphinx source folder found (conf.py and index.rst in docs/source, docs, doc/source, or doc/)")
            return None, False

        # Check if 'make' command is available
        if not shutil.which("make"):
            logger.error("'make' command not found on this system.")
            logger.error("Sphinx Makefile functionality requires GNU Make to be installed.")
            return None, False

        try:
            # Build Sphinx documentation using Makefile
            # Use the Makefile directory we found earlier
            if not makefile_dir:
                logger.error("Could not find Makefile directory")
                return None, False
            
            build_dir = self._build_via_makefile(makefile_dir, input_path)
            if not build_dir:
                logger.error("Failed to build Sphinx documentation using Makefile")
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
                logger.info(f"Markdown file created successfully: {markdown_output}")
                return markdown_output, True
            else:
                logger.warning(f"Markdown file not found at expected path: {markdown_output}")
                return None, False
                
        except Exception as e:
            logger.error(f"Sphinx Makefile conversion failed: {e}")
            return None, False

    def _build_via_makefile(self, makefile_dir: str, source_root: str) -> str | None:
        """Build Sphinx documentation using Makefile."""
        logger.info(f"Building Sphinx documentation using Makefile from: {makefile_dir}")
        
        try:
            # Create a temporary build directory
            build_dir = tempfile.mkdtemp(prefix="sphinx_makefile_build_")
            logger.info(f"Build directory: {build_dir}")
            
            # Run make clean and make html in the sphinx_source directory
            make_commands = [
                ["make", "clean"],
                ["make", "html"]
            ]
            
            for cmd in make_commands:
                logger.info(f"Running: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=makefile_dir  # Execute make commands in the directory containing the Makefile
                )
                
                if result.returncode != 0:
                    logger.warning(f"Command {' '.join(cmd)} failed with return code: {result.returncode}")
                    if result.stderr:
                        logger.warning(f"stderr: {result.stderr}")
                    # Continue anyway, as some files might have been generated
            
            # Check if HTML files were generated (try both common build directory names)
            html_dirs = [
                os.path.join(makefile_dir, "build", "html"),  # Standard Sphinx build directory
                os.path.join(makefile_dir, "_build", "html"),  # Alternative build directory
                os.path.join(makefile_dir, "html")  # Direct html directory
            ]
            
            html_dir = None
            for potential_dir in html_dirs:
                if os.path.exists(potential_dir):
                    html_dir = potential_dir
                    break
            
            if html_dir:
                logger.info(f"HTML build successful! Output in: {html_dir}")
                return html_dir
            else:
                logger.warning("HTML build directory not found in any expected location")
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
                out.write("## Sphinx Documentation\n\n")
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
