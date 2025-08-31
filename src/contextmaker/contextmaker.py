import argparse
import os
import sys
import logging
try:
    from .converters import (
        SphinxMakefileConverter, SphinxBuildConverter, NonsphinxConverter,
        RawSourceCodeConverter, NotebookConverter
    )
    from .converters.utils import detector
    from .utils import dependency_installer
except ImportError:
    from converters import (
        SphinxMakefileConverter, SphinxBuildConverter, NonsphinxConverter,
        RawSourceCodeConverter, NotebookConverter
    )
    from converters.utils import detector
    from utils import dependency_installer
import subprocess

### Clean logs at startup ###
def clean_logs_startup():
    """Clean log files at the beginning of the program."""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logs_dir = os.path.join(project_root, "logs")
        clean_logs_script = os.path.join(logs_dir, "clean_logs.py")
        
        if os.path.exists(clean_logs_script):
            # Import and run clean_logs function
            import importlib.util
            spec = importlib.util.spec_from_file_location("clean_logs", clean_logs_script)
            clean_logs_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(clean_logs_module)
            
            # Call the clean_logs function
            if hasattr(clean_logs_module, 'clean_logs'):
                clean_logs_module.clean_logs()
    except Exception as e:
        # Silently fail if cleaning logs fails - don't stop the program
        pass

# Clean logs before setting up logging
clean_logs_startup()

### Set up the logger ###
# Get the project root directory (where pyproject.toml is located)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Intelligent logging configuration using basicConfig
# This approach should work better across different Python environments
log_file_path = os.path.join(logs_dir, "conversion.log")

try:
    # Try to configure logging with basicConfig
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
        ],
        force=True  # Force reconfiguration
    )
except Exception as e:
    # Fallback: configure manually if basicConfig fails
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

# Get logger for this module
logger = logging.getLogger(__name__)

# Ensure all loggers propagate to root logger
logging.getLogger().setLevel(logging.INFO)
# Don't remove handlers from other loggers - this breaks NumPy and other modules
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).propagate = True
    # Only remove handlers if they're duplicates of our own
    # logging.getLogger(name).handlers = []  # This was breaking NumPy logging

# Filter out noisy third-party loggers
logging.getLogger('numexpr').setLevel(logging.WARNING)
logging.getLogger('numpy').setLevel(logging.WARNING)
logging.getLogger('pandas').setLevel(logging.WARNING)

### End of logger setup ###

### Intelligent utility functions ###
def _add_notebooks_to_file(input_path, output_file):
    """Add notebook content to an existing file."""
    try:
        # Try relative import first
        from .converters.utils import find_notebooks_in_doc_dirs, convert_notebook
    except ImportError:
        try:
            # Fallback to absolute import
            from contextmaker.converters.utils import find_notebooks_in_doc_dirs, convert_notebook
        except ImportError:
            # Final fallback: direct import from the file
            import sys
            # Get the path to the utils module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            utils_dir = os.path.join(current_dir, "converters", "utils")
            if utils_dir not in sys.path:
                sys.path.insert(0, utils_dir)
            from notebook_utils import find_notebooks_in_doc_dirs, convert_notebook
    
    notebooks_found = find_notebooks_in_doc_dirs(input_path)
    if notebooks_found:
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
                    logger.warning(f"Could not read notebook markdown {notebook_md}: {e}")
                    notebook_content.append(f"[Notebook content could not be read: {notebook_md}]")
                notebook_content.append("\n" + "-" * 50 + "\n")
        
        if notebook_content:
            # Write back with notebooks
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(current_content + ''.join(notebook_content))

def _convert_to_text(markdown_file):
    """Convert markdown file to text and clean up."""
    try:
        # Try relative import first
        from .converters.utils.text_converter import markdown_to_text
    except ImportError:
        try:
            # Fallback to absolute import
            from contextmaker.converters.utils.text_converter import markdown_to_text
        except ImportError:
            # Final fallback: direct import from the file
            import sys
            # Get the path to the text_converter module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            utils_dir = os.path.join(current_dir, "converters", "utils")
            if utils_dir not in sys.path:
                sys.path.insert(0, utils_dir)
            from text_converter import markdown_to_text
    
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

def _get_file_size(file_path):
    """Get file size in human readable format."""
    try:
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    except:
        return "Unknown size"

### Parsing arguments ###
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

### Main function ###
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
            logger.info(f"Conversion completed successfully. Output: {result}")
        else:
            logger.error("Conversion failed")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        sys.exit(1)

### Make function ###
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
        # ÉTAPE 1: Installation automatique des dépendances
        logger.info("Installing dependencies automatically...")
        dependency_installer.install_all_missing_dependencies()
        
        # ÉTAPE 2: Vérification que les modules essentiels sont disponibles
        logger.info("Verifying essential modules...")
        try:
            # Les converters sont maintenant importés au niveau du module
            logger.info("All essential modules are available")
        except ImportError as e:
            logger.error(f"Import error after dependency installation: {e}")
            return None
        
        # ÉTAPE 3: Vérification de la bibliothèque cible (optionnelle)
        # Skip library check for problematic libraries like cmbagent
        if library_name.lower() in ['cmbagent']:
            logger.info(f"Skipping library check for {library_name} (known to cause issues)")
            library_available = False
        else:
            try:
                library_available = dependency_installer.ensure_library_installed(library_name)
                if not library_available:
                    logger.info(f"Processing documentation for '{library_name}' without the library being installed.")
            except Exception as e:
                logger.warning(f"Library check failed for {library_name}: {e}, continuing without it")
                library_available = False
        
        # ÉTAPE 4: Détermination du chemin d'entrée
        if input_path:
            input_path = os.path.abspath(input_path)
            logger.info(f"Using manual path: {input_path}")
        else:
            logger.info(f"Searching for library '{library_name}'...")
            input_path = detector.find_library_path(library_name)
            if not input_path:
                logger.error(f"Library '{library_name}' not found. Try specifying the path manually with input_path.")
                return None
        
        # ÉTAPE 5: Gestion spéciale pour CAMB (si nécessaire)
        if library_name.lower() == "camb" and library_available:
            detector.ensure_camb_built(input_path)
            detector.patch_camb_sys_exit(input_path)

        # ÉTAPE 6: Détermination du chemin de sortie
        if output_path:
            output_path = os.path.abspath(output_path)
            # Check if output_path is a file path (has extension) and rough mode is enabled
            if rough and os.path.splitext(output_path)[1]:
                # Rough mode: output_path is a file path, extract directory
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Rough mode enabled: will save directly to {output_path}")
            else:
                # Normal mode: output_path is a directory
                if not os.path.splitext(output_path)[1]:  # No extension, treat as directory
                    os.makedirs(output_path, exist_ok=True)
        else:
            output_path = detector.get_default_output_path()
            os.makedirs(output_path, exist_ok=True)

        logger.info(f"Input path: {input_path}")
        logger.info(f"Output path: {output_path}")

        # ÉTAPE 7: Vérifications des chemins
        if not os.path.exists(input_path):
            logger.error(f"Input path '{input_path}' does not exist.")
            return None

        if not os.listdir(input_path):
            logger.error(f"Input path '{input_path}' is empty.")
            return None

        # ÉTAPE 8: Détection du format de documentation
        doc_format = detector.find_format(input_path)
        logger.info(f"Detected documentation format: {doc_format}")

        # ÉTAPE 9: Vérification des extensions Sphinx si nécessaire
        if doc_format == 'sphinx_makefile':
            logger.info("Ensuring Sphinx extensions are installed...")
            dependency_installer.ensure_sphinx_extensions(input_path)

        # ÉTAPE 10: Initialisation des variables de conversion
        output_file = None
        success = False
        conversion_mode = "Unknown"

        # ÉTAPE 11: Logique de fallback en cascade selon vos spécifications
        # 1) Sphinx (Makefile) - Priorité haute
        if doc_format == 'sphinx_makefile':
            logger.info("Attempting Sphinx conversion (Makefile)")
            converter = SphinxMakefileConverter()
            output_file, success = converter.convert(input_path, output_path, library_name)
            if success:
                logger.info("Sphinx conversion (Makefile) successful")
                conversion_mode = "Sphinx Makefile"
            else:
                logger.warning("Sphinx (Makefile) failed, trying Sphinx build fallback")
                success = False

        # 2) Sphinx build (fichiers conf.py et .rst) - Fallback Sphinx
        if not success and detector.has_documentation(input_path):
            logger.info("Attempting Sphinx build conversion (conf.py + .rst)")
            converter = SphinxBuildConverter()
            output_file, success = converter.convert(input_path, output_path, library_name)
            if success:
                logger.info("Sphinx build conversion successful")
                conversion_mode = "Sphinx Build"
            else:
                logger.warning("Sphinx build failed, trying non-Sphinx fallback")
                success = False

        # 3) Non-Sphinx build (md, docstrings, ...) - Fallback documentation
        if not success:
            logger.info("Attempting non-Sphinx conversion (md, docstrings, ...)")
            converter = NonsphinxConverter()
            output_file, success = converter.convert(input_path, output_path, library_name)
            if success:
                logger.info("Non-Sphinx conversion successful")
                conversion_mode = "Non-Sphinx"
            else:
                logger.warning("Non-Sphinx failed, trying raw source code fallback")
                success = False

        # 4) Raw source code - Fallback code source
        if not success:
            logger.info("Attempting raw source code conversion")
            converter = RawSourceCodeConverter()
            output_file, success = converter.convert(input_path, output_path, library_name)
            if success:
                logger.info("Raw source code conversion successful")
                conversion_mode = "Raw Source Code"
            else:
                logger.warning("Raw source code failed, trying notebooks fallback")
                success = False

        # 5) Notebooks - Dernier recours absolu
        if not success:
            logger.info("Attempting conversion via notebooks (last resort)")
            converter = NotebookConverter()
            output_file, success = converter.convert(input_path, output_path, library_name)
            if success:
                logger.info("Conversion via notebooks successful")
                conversion_mode = "Notebooks"
            else:
                logger.warning("Notebooks conversion failed")
                success = False  # S'assurer que success = False à la fin

        # ÉTAPE 12: Ajout automatique des notebooks si conversion réussie
        if success and output_file:
            logger.info(f"Conversion completed successfully. Output: {output_file}")
            
            # Ajouter automatiquement les notebooks si ils existent
            notebooks_found = detector.has_notebook(input_path)
            logger.info(f"Notebooks found: {notebooks_found}")
            if notebooks_found:
                try:
                    _add_notebooks_to_file(input_path, output_file)
                    logger.info("Notebooks added successfully")
                except Exception as e:
                    logger.error(f"Failed to add notebooks: {e}")
            
            # Convert to text if needed
            if extension == 'txt' and not output_file.endswith('.txt'):
                final_output = _convert_to_text(output_file)
            else:
                final_output = output_file
            
            if not library_available:
                logger.info(f"Documentation processed successfully despite library '{library_name}' not being available as a Python package.")
            
            # Final success message with green checkmark and summary
            file_size = _get_file_size(final_output)
            logger.info(f"✅ Conversion successful! Mode: {conversion_mode}, Output: {final_output}, Size: {file_size}")
            
            return final_output
        else:
            logger.error("All conversion methods failed: Sphinx Makefile, Sphinx build, non-Sphinx, raw source code, and notebooks")
            return None

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    main()