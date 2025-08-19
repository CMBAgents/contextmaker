"""
Dependency Manager for ContextMaker

This module provides comprehensive dependency management including:
- Python package dependencies
- System dependencies (Homebrew, apt, yum)
- Build tools installation
- Development mode installation
- Portable tools installation
"""

import os
import sys
import platform
import subprocess
import logging
import shutil
import tempfile
import urllib.request
import ssl
import zipfile
import tarfile
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
        self.portable_tools_dir = os.path.join(os.path.expanduser("~"), ".contextmaker", "portable_tools")
        
        # Ensure portable tools directory exists
        os.makedirs(self.portable_tools_dir, exist_ok=True)
        
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
        
        # Define portable tools with download URLs
        self.portable_tools = {
            'pandoc': {
                'darwin': {
                    'url': 'https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-arm64-macOS.zip',
                    'filename': 'pandoc-3.4-arm64-macOS.zip',
                    'extract_command': 'unzip',
                    'binary_name': 'pandoc'
                },
                'linux': {
                    'url': 'https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-linux-amd64.tar.gz',
                    'filename': 'pandoc-3.4-linux-amd64.tar.gz',
                    'extract_command': 'tar -xzf',
                    'binary_name': 'pandoc'
                },
                'windows': {
                    'url': 'https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-windows-x86_64.zip',
                    'filename': 'pandoc-3.4-windows-x86_64.zip',
                    'extract_command': 'unzip',
                    'binary_name': 'pandoc.exe'
                }
            },
            'cmake': {
                'darwin': {
                    'url': 'https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-macos-universal.tar.gz',
                    'filename': 'cmake-3.28.1-macos-universal.tar.gz',
                    'extract_command': 'tar -xzf',
                    'binary_name': 'cmake'
                },
                'linux': {
                    'url': 'https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-linux-x86_64.tar.gz',
                    'filename': 'cmake-3.28.1-linux-x86_64.tar.gz',
                    'extract_command': 'tar -xzf',
                    'binary_name': 'cmake'
                },
                'windows': {
                    'url': 'https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-windows-x86_64.zip',
                    'filename': 'cmake-3.28.1-windows-x86_64.zip',
                    'extract_command': 'unzip',
                    'binary_name': 'cmake.exe'
                }
            },
            'make': {
                'darwin': {
                    'url': None,  # Use system make on macOS
                    'filename': None,
                    'extract_command': None,
                    'binary_name': 'make'
                },
                'linux': {
                    'url': None,  # Use system make on Linux
                    'filename': None,
                    'extract_command': None,
                    'binary_name': 'make'
                },
                'windows': {
                    'url': None,  # Use system make on Windows if available
                    'filename': None,
                    'extract_command': None,
                    'binary_name': 'make.exe'
                }
            }
        }
        
        # Legacy system dependencies (kept for fallback)
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
    
    def download_file(self, url: str, filename: str) -> str:
        """
        Download a file from URL to the portable tools directory.
        
        Args:
            url (str): URL to download from
            filename (str): Name of the file to save
            
        Returns:
            str: Path to the downloaded file
        """
        file_path = os.path.join(self.portable_tools_dir, filename)
        
        if os.path.exists(file_path):
            logger.info(f"📁 File already exists: {file_path}")
            return file_path
        
        logger.info(f"⬇️ Downloading {filename} from {url}")
        
        try:
            # Create a context that ignores SSL certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Use urllib with SSL context
            with urllib.request.urlopen(url, context=ssl_context) as response:
                with open(file_path, 'wb') as f:
                    f.write(response.read())
            
            logger.info(f"✅ Downloaded: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Failed to download {filename}: {e}")
            return None
    
    def extract_portable_tool(self, tool_name: str, archive_path: str, extract_command: str = None) -> str:
        """
        Extract a portable tool from archive.
        
        Args:
            tool_name (str): Name of the tool
            archive_path (str): Path to the archive file
            extract_command (str): Command to extract the archive
            
        Returns:
            str: Path to the extracted binary, or None if failed
        """
        tool_dir = os.path.join(self.portable_tools_dir, tool_name)
        os.makedirs(tool_dir, exist_ok=True)
        
        try:
            if extract_command:
                # Use system command to extract
                if extract_command.startswith('tar'):
                    subprocess.run(f"cd {tool_dir} && {extract_command} {archive_path}", 
                                 shell=True, check=True)
                elif extract_command == 'unzip':
                    subprocess.run(f"cd {tool_dir} && unzip {archive_path}", 
                                 shell=True, check=True)
            else:
                # Use Python to extract
                if archive_path.endswith('.tar.gz'):
                    with tarfile.open(archive_path, 'r:gz') as tar:
                        tar.extractall(tool_dir)
                elif archive_path.endswith('.zip'):
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(tool_dir)
                elif archive_path.endswith('.pkg'):
                    # For macOS packages, we need to handle them differently
                    logger.info(f"📦 macOS package detected for {tool_name}, manual installation may be required")
                    return None
            
            # Find the binary in the extracted directory
            binary_name = self.portable_tools[tool_name][self.system]['binary_name']
            
            # Special handling for different archive structures
            if tool_name == 'pandoc':
                # Pandoc archives typically have a subdirectory with the version
                for root, dirs, files in os.walk(tool_dir):
                    if binary_name in files:
                        binary_path = os.path.join(root, binary_name)
                        # Make executable on Unix systems
                        if self.system != 'windows':
                            os.chmod(binary_path, 0o755)
                        logger.info(f"✅ Extracted {tool_name}: {binary_path}")
                        return binary_path
            else:
                # Standard extraction for other tools
                for root, dirs, files in os.walk(tool_dir):
                    if binary_name in files:
                        binary_path = os.path.join(root, binary_name)
                        # Make executable on Unix systems
                        if self.system != 'windows':
                            os.chmod(binary_path, 0o755)
                        logger.info(f"✅ Extracted {tool_name}: {binary_path}")
                        return binary_path
            
            logger.error(f"❌ Could not find {binary_name} in extracted files")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to extract {tool_name}: {e}")
            return None
    
    def install_portable_tool(self, tool_name: str) -> bool:
        """
        Install a portable tool.
        
        Args:
            tool_name (str): Name of the tool to install
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        if tool_name not in self.portable_tools:
            logger.error(f"❌ Unknown portable tool: {tool_name}")
            return False
        
        if self.system not in self.portable_tools[tool_name]:
            logger.error(f"❌ Tool {tool_name} not available for {self.system}")
            return False
        
        tool_info = self.portable_tools[tool_name][self.system]
        
        # Check if already installed
        binary_path = self.get_portable_tool_path(tool_name)
        if binary_path and os.path.exists(binary_path):
            logger.info(f"✅ {tool_name} already installed: {binary_path}")
            return True
        
        # For tools that use system binaries (like make on Unix)
        if tool_info['url'] is None:
            if shutil.which(tool_info['binary_name']):
                logger.info(f"✅ {tool_name} available from system: {shutil.which(tool_info['binary_name'])}")
                return True
            else:
                logger.error(f"❌ {tool_name} not available from system and no portable version provided")
                return False
        

        
        # Download and extract
        archive_path = self.download_file(tool_info['url'], tool_info['filename'])
        if not archive_path:
            return False
        
        binary_path = self.extract_portable_tool(tool_name, archive_path, tool_info['extract_command'])
        if not binary_path:
            return False
        
        # Clean up archive
        try:
            os.remove(archive_path)
        except:
            pass
        
        return True
    
    def get_portable_tool_path(self, tool_name: str) -> Optional[str]:
        """
        Get the path to a portable tool binary.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            Optional[str]: Path to the binary, or None if not found
        """
        if tool_name not in self.portable_tools:
            return None
        
        if self.system not in self.portable_tools[tool_name]:
            return None
        
        tool_info = self.portable_tools[tool_name][self.system]
        binary_name = tool_info['binary_name']
        
        # Check portable tools directory
        tool_dir = os.path.join(self.portable_tools_dir, tool_name)
        if os.path.exists(tool_dir):
            for root, dirs, files in os.walk(tool_dir):
                if binary_name in files:
                    return os.path.join(root, binary_name)
        
        # Check system PATH
        system_path = shutil.which(binary_name)
        if system_path:
            return system_path
        
        return None
    
    def install_portable_tools(self, tools: List[str] = None) -> bool:
        """
        Install portable tools.
        
        Args:
            tools (List[str]): List of tools to install. If None, installs all available tools.
            
        Returns:
            bool: True if all tools installed successfully, False otherwise
        """
        if tools is None:
            tools = list(self.portable_tools.keys())
        
        logger.info(f"🔧 Installing portable tools: {tools}")
        
        success_count = 0
        for tool in tools:
            if self.install_portable_tool(tool):
                success_count += 1
            else:
                logger.warning(f"⚠️ Failed to install portable tool: {tool}")
        
        if success_count == len(tools):
            logger.info(f"✅ All {len(tools)} portable tools installed successfully")
            return True
        else:
            logger.warning(f"⚠️ Only {success_count}/{len(tools)} portable tools installed")
            return False
    
    def install_pandoc_macos(self) -> bool:
        """
        Install Pandoc on macOS using Homebrew as fallback.
        
        Returns:
            bool: True if installation successful, False otherwise
        """
        logger.info("🍺 Trying to install Pandoc via Homebrew...")
        
        try:
            # Check if Homebrew is available
            if not shutil.which('brew'):
                logger.error("❌ Homebrew not found. Please install Homebrew first: https://brew.sh")
                return False
            
            # Install Pandoc via Homebrew
            result = subprocess.run(['brew', 'install', 'pandoc'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Pandoc installed successfully via Homebrew")
                return True
            else:
                logger.error(f"❌ Failed to install Pandoc via Homebrew: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Timeout installing Pandoc via Homebrew")
            return False
        except Exception as e:
            logger.error(f"❌ Error installing Pandoc via Homebrew: {e}")
            return False
    
    def cleanup_portable_tools(self):
        """
        Clean up portable tools directory and downloaded files.
        """
        try:
            if os.path.exists(self.portable_tools_dir):
                import shutil
                shutil.rmtree(self.portable_tools_dir)
                logger.info(f"🧹 Cleaned up portable tools directory: {self.portable_tools_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup portable tools: {e}")
    
    def list_installed_portable_tools(self) -> List[str]:
        """
        List all installed portable tools.
        
        Returns:
            List[str]: List of installed tool names
        """
        installed_tools = []
        for tool_name in self.portable_tools.keys():
            if self.check_portable_tool_available(tool_name):
                installed_tools.append(tool_name)
        return installed_tools
    
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
    
    def get_tool_command(self, tool_name: str) -> Optional[str]:
        """
        Get the full command path for a tool, preferring portable installation.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            Optional[str]: Full path to the tool command, or None if not found
        """
        # First check portable installation
        portable_path = self.get_portable_tool_path(tool_name)
        if portable_path and os.path.exists(portable_path):
            return portable_path
        
        # Fallback to system PATH
        return shutil.which(tool_name)
    
    def run_portable_command(self, tool_name: str, args: List[str], **kwargs) -> subprocess.CompletedProcess:
        """
        Run a command using portable tool if available, fallback to system tool.
        
        Args:
            tool_name (str): Name of the tool to run
            args (List[str]): Arguments to pass to the tool
            **kwargs: Additional arguments for subprocess.run
            
        Returns:
            subprocess.CompletedProcess: Result of the command execution
        """
        command_path = self.get_tool_command(tool_name)
        if not command_path:
            raise FileNotFoundError(f"Tool '{tool_name}' not found")
        
        full_command = [command_path] + args
        logger.info(f"🔧 Running command: {' '.join(full_command)}")
        
        return subprocess.run(full_command, **kwargs)
    
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
        Ensure all required build tools are installed using portable installation.
        
        Returns:
            bool: True if all tools are available, False otherwise
        """
        # Define essential build tools that we need
        essential_tools = ['pandoc', 'cmake']
        
        # Add make for Unix systems (use system make if available)
        if self.system in ['darwin', 'linux']:
            essential_tools.append('make')
        
        logger.info(f"🔧 Ensuring portable build tools: {essential_tools}")
        
        # Try portable installation first
        portable_success = self.install_portable_tools(essential_tools)
        
        if portable_success:
            logger.info("✅ All essential build tools installed via portable method")
            return True
        
        # Check which tools are still missing
        missing_tools = []
        for tool in essential_tools:
            if not self.check_portable_tool_available(tool):
                missing_tools.append(tool)
        
        if not missing_tools:
            logger.info("✅ All build tools are available")
            return True
        
        logger.warning(f"⚠️ Some tools could not be installed portably: {missing_tools}")
        logger.info("💡 You may need to install these tools manually or use system package managers")
        
        # Return True if at least some tools are available
        available_tools = len(essential_tools) - len(missing_tools)
        if available_tools > 0:
            logger.info(f"✅ {available_tools}/{len(essential_tools)} build tools are available")
            return True
        else:
            logger.error("❌ No build tools are available")
            return False
    
    def check_portable_tool_available(self, tool_name: str) -> bool:
        """
        Check if a portable tool is available.
        
        Args:
            tool_name (str): Name of the tool to check
            
        Returns:
            bool: True if tool is available, False otherwise
        """
        # Check portable installation first
        portable_path = self.get_portable_tool_path(tool_name)
        if portable_path and os.path.exists(portable_path):
            return True
        
        # Check system PATH as fallback
        if tool_name in self.portable_tools:
            binary_name = self.portable_tools[tool_name][self.system]['binary_name']
            return shutil.which(binary_name) is not None
        
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

    def detect_sphinx_extensions(self, conf_path: str) -> List[str]:
        """
        Parse conf.py to detect required Sphinx extensions.
        
        Args:
            conf_path (str): Path to the Sphinx conf.py file
            
        Returns:
            List[str]: List of required Sphinx extension names
        """
        extensions = []
        
        if not os.path.exists(conf_path):
            logger.warning(f"⚠️ Sphinx conf.py not found at: {conf_path}")
            return extensions
        
        try:
            with open(conf_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Common patterns for extensions in conf.py
            import re
            
            # Pattern 1: extensions = ['ext1', 'ext2', ...]
            pattern1 = r'extensions\s*=\s*\[(.*?)\]'
            matches = re.findall(pattern1, content, re.DOTALL)
            
            for match in matches:
                # Extract extension names from the list
                ext_names = re.findall(r"['\"]([^'\"]+)['\"]", match)
                extensions.extend(ext_names)
            
            # Pattern 2: extensions.append('ext_name')
            pattern2 = r'extensions\.append\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(pattern2, content)
            extensions.extend(matches)
            
            # Pattern 3: extensions += ['ext1', 'ext2']
            pattern3 = r'extensions\s*\+=\s*\[(.*?)\]'
            matches = re.findall(pattern3, content, re.DOTALL)
            for match in matches:
                ext_names = re.findall(r"['\"]([^'\"]+)['\"]", match)
                extensions.extend(ext_names)
            
            # Remove duplicates and filter out built-in extensions
            built_in_extensions = {
                'sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon',
                'sphinx.ext.todo', 'sphinx.ext.coverage', 'sphinx.ext.mathjax',
                'sphinx.ext.ifconfig', 'sphinx.ext.githubpages', 'sphinx.ext.intersphinx'
            }
            
            unique_extensions = []
            for ext in extensions:
                if ext not in built_in_extensions and ext not in unique_extensions:
                    unique_extensions.append(ext)
            
            logger.info(f"🔍 Detected {len(unique_extensions)} Sphinx extensions: {unique_extensions}")
            return unique_extensions
            
        except Exception as e:
            logger.error(f"❌ Error detecting Sphinx extensions: {e}")
            return extensions

    def ensure_sphinx_extensions(self, project_path: str) -> bool:
        """
        Ensure all required Sphinx extensions for a project are installed.
        
        Args:
            project_path (str): Path to the project root directory
            
        Returns:
            bool: True if all extensions are available, False otherwise
        """
        logger.info(f"🔍 Checking Sphinx extensions for project: {project_path}")
        
        # Look for conf.py in common locations
        conf_locations = [
            os.path.join(project_path, 'docs', 'conf.py'),
            os.path.join(project_path, 'doc', 'conf.py'),
            os.path.join(project_path, 'conf.py'),
            os.path.join(project_path, 'sphinx', 'conf.py')
        ]
        
        conf_path = None
        for loc in conf_locations:
            if os.path.exists(loc):
                conf_path = loc
                break
        
        if not conf_path:
            logger.info(f"ℹ️ No Sphinx conf.py found in project: {project_path}")
            return True  # Not a Sphinx project, so no extensions needed
        
        # Detect required extensions from conf.py
        detected_extensions = self.detect_sphinx_extensions(conf_path)
        
        # Add commonly needed extensions that are often missing
        common_extensions = [
            "sphinx_copybutton",  # Very commonly used for copy buttons
            "sphinx_rtd_theme",   # Read the Docs theme
            "sphinx.ext.autodoc", # Auto-documentation
            "sphinx.ext.napoleon", # Google/NumPy docstring support
            "shapely",            # Geometry library often needed for examples
            "scikit-image",       # Image processing library (skimage) often needed for examples
            "sphinx_automodapi"   # Auto-module API generation (used by astropy projects)
        ]
        
        # Combine detected and common extensions, removing duplicates
        all_extensions = list(dict.fromkeys(detected_extensions + common_extensions))
        
        logger.info(f"🔍 Checking {len(all_extensions)} Sphinx extensions (detected: {len(detected_extensions)}, common: {len(common_extensions)})")
        
        # Check and install missing extensions
        missing_extensions = []
        for ext in all_extensions:
            if not self.check_python_package(ext):
                missing_extensions.append(ext)
        
        if not missing_extensions:
            logger.info(f"✅ All Sphinx extensions are already installed")
            return True
        
        # Install missing extensions
        logger.info(f"📦 Installing {len(missing_extensions)} missing Sphinx extensions: {missing_extensions}")
        
        success_count = 0
        for ext in missing_extensions:
            if self.install_python_package(ext):
                success_count += 1
            else:
                logger.warning(f"⚠️ Failed to install Sphinx extension: {ext}")
        
        if success_count == len(missing_extensions):
            logger.info(f"✅ All Sphinx extensions installed successfully")
            return True
        else:
            logger.warning(f"⚠️ Only {success_count}/{len(missing_extensions)} Sphinx extensions were installed")
            return False

    def get_common_sphinx_extensions(self) -> List[str]:
        """
        Get a list of commonly used Sphinx extensions that might be needed.
        
        Returns:
            List[str]: List of common Sphinx extension names
        """
        return [
            "sphinx_copybutton",
            "sphinx_rtd_theme",
            "sphinx.ext.autodoc",
            "sphinx.ext.napoleon",
            "sphinx.ext.viewcode",
            "sphinx.ext.todo",
            "sphinx.ext.coverage",
            "sphinx.ext.mathjax",
            "sphinx.ext.ifconfig",
            "sphinx.ext.githubpages",
            "sphinx.ext.intersphinx",
            "sphinx.ext.autosummary",
            "sphinx.ext.doctest",
            "sphinx.ext.imgmath",
            "sphinx.ext.graphviz",
            "sphinx.ext.inheritance_diagram",
            "sphinx.ext.linkcode",
            "sphinx.ext.extlinks",
            "sphinx.ext.issue",
            "sphinx.ext.warning",
            "sphinx.ext.duration",
            "sphinx.ext.autosectionlabel",
            "sphinx.ext.tabs",
            "sphinx_panels",
            "sphinx_tabs.tabs",
            "sphinx_automodapi.automodapi",
            "sphinx_automodapi.smart_resolver",
            "sphinx_gallery.gen_gallery",
            "nbsphinx",
            "myst_parser",
            "sphinxcontrib.bibtex",
            "sphinxcontrib.programoutput",
            "sphinxcontrib.plantuml",
            "sphinxcontrib.websupport",
            "sphinxcontrib.applehelp",
            "sphinxcontrib.devhelp",
            "sphinxcontrib.htmlhelp",
            "sphinxcontrib.jsmath",
            "sphinxcontrib.qthelp",
            "sphinxcontrib.serializinghtml"
        ]


# Global instance for easy access
dependency_manager = DependencyManager()
