from .contextmaker import make  # Expose 'make' as the main API, keep 'convert' for backward compatibility

# The make function now supports a 'rough' parameter for direct file output
# Usage: make(library_name, output_path="/path/to/file.txt", rough=True)
