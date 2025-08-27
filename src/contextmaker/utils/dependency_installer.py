"""
Universal Dependency Installer for ContextMaker

Automatically detects and installs ALL missing dependencies via pip.
Provides clear logging without emojis (except for fallbacks).
"""

import subprocess
import sys
import importlib
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class UniversalDependencyInstaller:
    """
    Automatically installs ALL missing dependencies via pip.
    Provides clear logging and robust error handling.
    """
    
    def __init__(self):
        self.required_packages = [
            "sphinx",
            "jupytext", 
            "sphinx-rtd-theme",
            "myst-parser",
            "sphinx-markdown-builder",
            "markdownify",
            "rich",
            "beautifulsoup4",
            "html2text",
            "markdown",
            "numpy",
            "docutils",
            "jinja2",
            "pygments",
            "nbformat",
            "nbconvert",
            "jupyter"
        ]
        
        self.optional_packages = [
            "pandoc",
            "cmake"
        ]
        
        self.installed_packages = set()
        self.failed_packages = set()
    
    def check_pip_available(self) -> bool:
        """Check if pip is available and working."""
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is already installed."""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
    
    def install_package(self, package_name: str) -> bool:
        """Install a single package via pip."""
        try:
            logger.info(f"{package_name} → Manquant → Installation...")
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"{package_name} → Installé avec succès")
                self.installed_packages.add(package_name)
                return True
            else:
                logger.warning(f"{package_name} → Échec d'installation: {result.stderr}")
                self.failed_packages.add(package_name)
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning(f"{package_name} → Échec d'installation: Timeout")
            self.failed_packages.add(package_name)
            return False
        except Exception as e:
            logger.warning(f"{package_name} → Échec d'installation: {e}")
            self.failed_packages.add(package_name)
            return False
    
    def install_all_missing_dependencies(self) -> Dict[str, List[str]]:
        """
        Install ALL missing dependencies automatically.
        
        Returns:
            Dict with 'installed' and 'failed' package lists
        """
        logger.info("Vérification des dépendances...")
        
        # Check if pip is available
        if not self.check_pip_available():
            logger.error("pip n'est pas disponible. Installation automatique impossible.")
            return {"installed": [], "failed": self.required_packages}
        
        # Check required packages
        for package in self.required_packages:
            if not self.is_package_installed(package):
                self.install_package(package)
            else:
                logger.info(f"{package} → Déjà installé")
        
        # Check optional packages
        for package in self.optional_packages:
            if not self.is_package_installed(package):
                self.install_package(package)
            else:
                logger.info(f"{package} → Déjà installé")
        
        # Summary
        if self.installed_packages:
            logger.info(f"Packages installés: {', '.join(self.installed_packages)}")
        
        if self.failed_packages:
            logger.warning(f"Packages en échec: {', '.join(self.failed_packages)}")
        
        return {
            "installed": list(self.installed_packages),
            "failed": list(self.failed_packages)
        }
    
    def ensure_sphinx_extensions(self, project_path: str) -> bool:
        """
        Ensure all required Sphinx extensions are installed for a project.
        
        Args:
            project_path: Path to the Sphinx project
            
        Returns:
            True if all extensions are available, False otherwise
        """
        try:
            # Try to import sphinx
            import sphinx
            logger.info("Sphinx disponible")
            return True
        except ImportError:
            logger.warning("Sphinx non disponible, tentative d'installation...")
            return self.install_package("sphinx")
    
    def ensure_library_installed(self, library_name: str) -> bool:
        """
        Try to ensure a library is installed, but continue if it fails.
        
        Args:
            library_name: Name of the library to check
            
        Returns:
            True if library is available, False otherwise
        """
        try:
            importlib.import_module(library_name)
            logger.info(f"Bibliothèque {library_name} disponible")
            return True
        except ImportError:
            logger.info(f"Bibliothèque {library_name} non disponible, continuation sans installation")
            return False


# Global instance for easy access
dependency_installer = UniversalDependencyInstaller()
