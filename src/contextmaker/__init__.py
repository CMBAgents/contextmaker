from .contextmaker import make  # Expose 'make' as the main API, keep 'convert' for backward compatibility

# The make function now supports a 'rough' parameter for direct file output
# Usage: make(library_name, output_path="/path/to/file.txt", rough=True)

# New dependency and build management
from .dependency_manager import DependencyManager, dependency_manager
from .build_manager import BuildManager, build_manager

__all__ = [
    'make',
    'DependencyManager', 
    'dependency_manager',
    'BuildManager',
    'build_manager'
]
