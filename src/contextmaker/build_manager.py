"""
Build Manager for ContextMaker

This module provides enhanced build management including:
- Build process orchestration
- Output validation
- Error handling and retry logic
- Build directory management
"""

import os
import sys
import logging
import shutil
import glob
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path

from .dependency_manager import dependency_manager

logger = logging.getLogger(__name__)


class BuildManager:
    """
    Enhanced build manager for ContextMaker.
    Handles build process orchestration, validation, and error recovery.
    """
    
    def __init__(self):
        self.temp_dirs = []
    
    def validate_build_output(self, build_dir: str, expected_formats: List[str] = None) -> bool:
        """
        Validate that a build directory contains expected output files.
        
        Args:
            build_dir (str): Path to the build directory
            expected_formats (List[str]): List of expected file extensions (e.g., ['txt', 'html'])
            
        Returns:
            bool: True if build output is valid, False otherwise
        """
        if not os.path.exists(build_dir):
            logger.error(f"❌ Build directory does not exist: {build_dir}")
            return False
        
        if not os.path.isdir(build_dir):
            logger.error(f"❌ Build path is not a directory: {build_dir}")
            return False
        
        # Check if directory is empty
        if not os.listdir(build_dir):
            logger.error(f"❌ Build directory is empty: {build_dir}")
            return False
        
        # If expected formats are specified, check for them
        if expected_formats:
            found_files = []
            for ext in expected_formats:
                pattern = os.path.join(build_dir, f"**/*.{ext}")
                files = glob.glob(pattern, recursive=True)
                found_files.extend(files)
            
            if not found_files:
                logger.error(f"❌ No files with expected formats {expected_formats} found in {build_dir}")
                return False
            
            logger.info(f"✅ Found {len(found_files)} files with expected formats in {build_dir}")
        
        # Check for common build artifacts
        common_artifacts = ['index.txt', 'index.html', 'doctrees', '_build']
        found_artifacts = []
        
        for artifact in common_artifacts:
            artifact_path = os.path.join(build_dir, artifact)
            if os.path.exists(artifact_path):
                found_artifacts.append(artifact)
        
        if found_artifacts:
            logger.info(f"✅ Found build artifacts: {found_artifacts}")
        else:
            logger.warning(f"⚠️ No common build artifacts found in {build_dir}")
        
        return True
    
    def cleanup_build_directory(self, build_dir: str) -> bool:
        """
        Clean up a build directory safely.
        
        Args:
            build_dir (str): Path to the build directory to clean
            
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        try:
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
                logger.info(f"🧹 Cleaned up build directory: {build_dir}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clean up build directory {build_dir}: {e}")
            return False
    
    def create_temp_build_dir(self, prefix: str = "contextmaker_build_") -> str:
        """
        Create a temporary build directory.
        
        Args:
            prefix (str): Prefix for the temporary directory name
            
        Returns:
            str: Path to the created temporary directory
        """
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self.temp_dirs.append(temp_dir)
        logger.debug(f"📁 Created temporary build directory: {temp_dir}")
        return temp_dir
    
    def cleanup_all_temp_dirs(self):
        """Clean up all temporary directories created by this instance."""
        for temp_dir in self.temp_dirs:
            self.cleanup_build_directory(temp_dir)
        self.temp_dirs.clear()
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup_all_temp_dirs()
    
    def build_with_validation(self, build_func, *args, validate_output: bool = True, 
                            expected_formats: List[str] = None, max_retries: int = 3, **kwargs) -> Optional[str]:
        """
        Execute a build function with validation and retry logic.
        
        Args:
            build_func: Function to execute for building
            *args: Arguments for build_func
            validate_output (bool): Whether to validate the build output
            expected_formats (List[str]): Expected file formats for validation
            max_retries (int): Maximum number of retry attempts
            **kwargs: Keyword arguments for build_func
            
        Returns:
            str | None: Path to build directory if successful, None otherwise
        """
        return dependency_manager.retry_build_with_dependencies(
            self._build_with_validation_internal,
            build_func, *args,
            validate_output=validate_output,
            expected_formats=expected_formats,
            **kwargs
        )
    
    def _build_with_validation_internal(self, build_func, *args, validate_output: bool = True,
                                      expected_formats: List[str] = None, **kwargs) -> Optional[str]:
        """
        Internal method for build with validation.
        
        Args:
            build_func: Function to execute for building
            *args: Arguments for build_func
            validate_output (bool): Whether to validate the build output
            expected_formats (List[str]): Expected file formats for validation
            **kwargs: Keyword arguments for build_func
            
        Returns:
            str | None: Path to build directory if successful, None otherwise
        """
        try:
            # Execute the build function
            build_dir = build_func(*args, **kwargs)
            
            if not build_dir:
                logger.error("❌ Build function returned None")
                return None
            
            # Validate the build output if requested
            if validate_output:
                if not self.validate_build_output(build_dir, expected_formats):
                    logger.error("❌ Build output validation failed")
                    return None
            
            logger.info(f"✅ Build completed successfully: {build_dir}")
            return build_dir
            
        except Exception as e:
            logger.error(f"❌ Build failed with exception: {e}")
            return None
    
    def ensure_build_environment(self, source_root: str = None) -> bool:
        """
        Ensure the build environment is properly set up.
        
        Args:
            source_root (str): Path to the source root directory
            
        Returns:
            bool: True if environment is ready, False otherwise
        """
        try:
            with dependency_manager.setup_environment(source_root):
                logger.info("✅ Build environment setup completed")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to setup build environment: {e}")
            return False
    
    def find_build_artifacts(self, build_dir: str, file_patterns: List[str] = None) -> List[str]:
        """
        Find build artifacts in a build directory.
        
        Args:
            build_dir (str): Path to the build directory
            file_patterns (List[str]): List of file patterns to search for
            
        Returns:
            List[str]: List of found file paths
        """
        if not file_patterns:
            file_patterns = ['*.txt', '*.html', '*.md']
        
        found_files = []
        for pattern in file_patterns:
            pattern_path = os.path.join(build_dir, '**', pattern)
            files = glob.glob(pattern_path, recursive=True)
            found_files.extend(files)
        
        return found_files
    
    def check_build_success(self, build_dir: str, min_files: int = 1) -> bool:
        """
        Check if a build was successful based on file count.
        
        Args:
            build_dir (str): Path to the build directory
            min_files (int): Minimum number of files expected
            
        Returns:
            bool: True if build appears successful, False otherwise
        """
        if not os.path.exists(build_dir):
            return False
        
        # Count all files in the build directory
        file_count = 0
        for root, dirs, files in os.walk(build_dir):
            file_count += len(files)
        
        if file_count >= min_files:
            logger.info(f"✅ Build appears successful with {file_count} files")
            return True
        else:
            logger.warning(f"⚠️ Build may have failed - only {file_count} files found (expected >= {min_files})")
            return False


# Global instance for easy access
build_manager = BuildManager()
