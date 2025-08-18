"""
Dependency Manager for ContextMaker

This module provides comprehensive dependency management including:
- Python package dependencies
- System dependencies (Homebrew, apt, yum)
- Build tools installation
- Development mode installation
"""

import os
import sys
import platform
import subprocess
import logging
import shutil
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DependencyManager:
    """
    Comprehensive dependency manager for ContextMaker.
    Handles Python packages, system dependencies, and build tools.
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        self.required_python_packages = [
            "sphinx>=5.0.0",
            "jupytext>=1.14.0", 
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=1.0.0",
            "sphinx-markdown-builder>=0.6.5",
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
        
        self.system_dependencies = {
            'darwin': {  # macOS
                'build_tools': ['pkg-config', 'autoconf', 'automake', 'libtool', 'cmake'],
                'package_manager': 'brew'
            },
            'linux': {  # Linux
                'build_tools': ['pkg-config', 'autoconf', 'automake', 'libtool', 'cmake', 'build-essential'],
                'package_manager': self._detect_linux_package_manager()
            },
            'windows': {  # Windows
                'build_tools': ['cmake'],
                'package_manager': 'chocolatey'  # or winget
            }
        }
    
    def _detect_linux_package_manager(self) -> str:
        """Detect the Linux package manager."""
        if shutil.which("apt"):
            return "apt"
        elif shutil.which("yum"):
            return "yum"
        elif shutil.which("dnf"):
            return "dnf"
        elif shutil.which("pacman"):
            return "pacman"
        else:
            return "unknown"
    
    def check_python_package(self, package_name: str) -> bool:
        """
        Check if a Python package is installed.
        
        Args:
            package_name (str): Name of the package to check
            
        Returns:
            bool: True if package is available, False otherwise
        """
        try:
            __import__(package_name.replace('-', '_').split('>=')[0].split('==')[0])
            return True
        except ImportError:
            return False
    
    def install_python_package(self, package_name: str, timeout: int = 120) -> bool:
        """
        Install a Python package using pip.
        
        Args:
            package_name (str): Package name to install
            timeout (int): Timeout in seconds
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        logger.info(f"📦 Installing Python package: {package_name}")
        
        try:
            cmd = [self.python_executable, "-m", "pip", "install", package_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully installed: {package_name}")
                return True
            else:
                logger.error(f"❌ Failed to install {package_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout installing {package_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error installing {package_name}: {e}")
            return False
    
    def install_python_package_dev(self, package_path: str, timeout: int = 120) -> bool:
        """
        Install a Python package in development mode.
        
        Args:
            package_path (str): Path to the package directory
            timeout (int): Timeout in seconds
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        logger.info(f"🔧 Installing package in development mode: {package_path}")
        
        try:
            cmd = [self.python_executable, "-m", "pip", "install", "-e", package_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=package_path
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully installed in dev mode: {package_path}")
                return True
            else:
                logger.error(f"❌ Failed to install in dev mode {package_path}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout installing in dev mode: {package_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Error installing in dev mode {package_path}: {e}")
            return False
    
    def check_system_package(self, package_name: str) -> bool:
        """
        Check if a system package is installed.
        
        Args:
            package_name (str): Name of the system package
            
        Returns:
            bool: True if package is available, False otherwise
        """
        return shutil.which(package_name) is not None
    
    def install_system_package(self, package_name: str, timeout: int = 300) -> bool:
        """
        Install a system package using the appropriate package manager.
        
        Args:
            package_name (str): Name of the package to install
            timeout (int): Timeout in seconds
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        if self.system not in self.system_dependencies:
            logger.error(f"❌ Unsupported system: {self.system}")
            return False
        
        package_manager = self.system_dependencies[self.system]['package_manager']
        
        if package_manager == 'unknown':
            logger.error(f"❌ Could not detect package manager for {self.system}")
            return False
        
        logger.info(f"🔧 Installing system package: {package_name} using {package_manager}")
        
        try:
            if package_manager == 'brew':
                cmd = ['brew', 'install', package_name]
            elif package_manager == 'apt':
                cmd = ['sudo', 'apt-get', 'update'] + ['sudo', 'apt-get', 'install', '-y', package_name]
            elif package_manager == 'yum':
                cmd = ['sudo', 'yum', 'install', '-y', package_name]
            elif package_manager == 'dnf':
                cmd = ['sudo', 'dnf', 'install', '-y', package_name]
            elif package_manager == 'pacman':
                cmd = ['sudo', 'pacman', '-S', '--noconfirm', package_name]
            elif package_manager == 'chocolatey':
                cmd = ['choco', 'install', package_name, '-y']
            else:
                logger.error(f"❌ Unsupported package manager: {package_manager}")
                return False
            
            # Handle apt-get update separately
            if package_manager == 'apt':
                update_cmd = ['sudo', 'apt-get', 'update']
                update_result = subprocess.run(update_cmd, capture_output=True, text=True, timeout=60)
                if update_result.returncode != 0:
                    logger.warning(f"⚠️ Package list update failed: {update_result.stderr}")
                
                # Now install the package
                install_cmd = ['sudo', 'apt-get', 'install', '-y', package_name]
                result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=timeout)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully installed system package: {package_name}")
                return True
            else:
                logger.error(f"❌ Failed to install system package {package_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout installing system package: {package_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error installing system package {package_name}: {e}")
            return False
    
    def ensure_build_tools(self) -> bool:
        """
        Ensure all required build tools are installed.
        
        Returns:
            bool: True if all tools are available, False otherwise
        """
        if self.system not in self.system_dependencies:
            logger.error(f"❌ Unsupported system: {self.system}")
            return False
        
        build_tools = self.system_dependencies[self.system]['build_tools']
        missing_tools = []
        
        # Check which tools are missing
        for tool in build_tools:
            if not self.check_system_package(tool):
                missing_tools.append(tool)
        
        if not missing_tools:
            logger.info("✅ All build tools are already installed")
            return True
        
        logger.info(f"🔧 Installing missing build tools: {missing_tools}")
        
        # Install missing tools
        success_count = 0
        for tool in missing_tools:
            if self.install_system_package(tool):
                success_count += 1
        
        if success_count == len(missing_tools):
            logger.info("✅ All build tools installed successfully")
            return True
        else:
            logger.warning(f"⚠️ Only {success_count}/{len(missing_tools)} build tools installed")
            return False
    
    def ensure_python_dependencies(self) -> bool:
        """
        Ensure all required Python packages are installed.
        
        Returns:
            bool: True if all packages are available, False otherwise
        """
        missing_packages = []
        
        # Check which packages are missing
        for package in self.required_python_packages:
            package_name = package.split('>=')[0].split('==')[0]
            if not self.check_python_package(package_name):
                missing_packages.append(package)
        
        if not missing_packages:
            logger.info("✅ All Python dependencies are already installed")
            return True
        
        logger.info(f"📦 Installing missing Python packages: {missing_packages}")
        
        # Install missing packages
        success_count = 0
        for package in missing_packages:
            if self.install_python_package(package):
                success_count += 1
        
        if success_count == len(missing_packages):
            logger.info("✅ All Python dependencies installed successfully")
            return True
        else:
            logger.warning(f"⚠️ Only {success_count}/{len(missing_packages)} Python packages installed")
            return False
    
    def ensure_library_installed(self, library_name: str, install_dev: bool = False) -> bool:
        """
        Enhanced version of ensure_library_installed with better error handling and retry logic.
        
        Args:
            library_name (str): Name of the library to install
            install_dev (bool): Whether to try development mode installation
            
        Returns:
            bool: True if library is available, False otherwise
        """
        # First check if already available
        try:
            __import__(library_name)
            logger.info(f"✅ Library '{library_name}' is already available")
            return True
        except ImportError:
            pass
        
        logger.info(f"📦 Library '{library_name}' not found. Attempting installation...")
        
        # Try regular pip installation first
        if self.install_python_package(library_name):
            try:
                __import__(library_name)
                logger.info(f"✅ Library '{library_name}' successfully installed and imported")
                return True
            except ImportError:
                logger.warning(f"⚠️ Library '{library_name}' was installed but could not be imported")
        
        # If regular installation failed and dev mode is requested, try development installation
        if install_dev:
            logger.info(f"🔧 Trying development mode installation for '{library_name}'...")
            # This would require finding the library source directory
            # For now, we'll just log that this feature is available
            logger.info(f"💡 Development mode installation requires manual path specification")
        
        logger.warning(f"⚠️ Could not install '{library_name}'. Continuing with documentation processing...")
        return False
    
    @contextmanager
    def setup_environment(self, source_root: str = None):
        """
        Context manager to set up the environment for building.
        
        Args:
            source_root (str): Path to the source root directory
        """
        original_env = os.environ.copy()
        
        try:
            # Ensure all dependencies are available
            logger.info("🔧 Setting up build environment...")
            
            # Install build tools
            if not self.ensure_build_tools():
                logger.warning("⚠️ Some build tools could not be installed")
            
            # Install Python dependencies
            if not self.ensure_python_dependencies():
                logger.warning("⚠️ Some Python dependencies could not be installed")
            
            # Set up PYTHONPATH if source_root is provided
            if source_root:
                current_pythonpath = os.environ.get("PYTHONPATH", "")
                new_pythonpath = f"{source_root}{os.pathsep}{current_pythonpath}" if current_pythonpath else source_root
                os.environ["PYTHONPATH"] = new_pythonpath
                logger.info(f"🔧 Set PYTHONPATH: {new_pythonpath}")
            
            yield
            
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def retry_build_with_dependencies(self, build_func, *args, max_retries: int = 3, **kwargs):
        """
        Retry a build function with dependency installation between attempts.
        
        Args:
            build_func: Function to retry
            *args: Arguments for build_func
            max_retries (int): Maximum number of retry attempts
            **kwargs: Keyword arguments for build_func
            
        Returns:
            Result of build_func if successful, None otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"🔧 Build attempt {attempt + 1}/{max_retries}")
                result = build_func(*args, **kwargs)
                
                if result:
                    logger.info(f"✅ Build successful on attempt {attempt + 1}")
                    return result
                
                # If build failed, try to install missing dependencies
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Build failed, ensuring dependencies before retry...")
                    self.ensure_python_dependencies()
                    self.ensure_build_tools()
                
            except Exception as e:
                logger.error(f"❌ Build attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying after dependency check...")
                    self.ensure_python_dependencies()
                    self.ensure_build_tools()
        
        logger.error(f"❌ All {max_retries} build attempts failed")
        return None


# Global instance for easy access
dependency_manager = DependencyManager()
