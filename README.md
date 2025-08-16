# ContextMaker

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

**ContextMaker** is a powerful Python toolkit that converts library documentation into formats optimized for AI agent ingestion. It automatically detects and processes various documentation formats including Sphinx, Jupyter notebooks, Python docstrings, and raw source code.

**Feature to enrich the CMBAgents:** Multi-Agent System for Science, Made by Cosmologists, Powered by [AG2](https://github.com/ag2ai/ag2).

## Features

- 🔍 **Automatic Format Detection**: Intelligently detects Sphinx, notebooks, docstrings, or source code
- 📚 **Multi-Format Support**: Handles Sphinx documentation, Jupyter notebooks, Python docstrings, and raw source
- 🚀 **Smart Fallbacks**: Multiple conversion methods with automatic fallbacks for maximum compatibility
- 📝 **Flexible Output**: Generate clean text (.txt) or markdown (.md) files
- 🎯 **AI-Optimized**: Output formatted specifically for Large Language Model ingestion
- 🔧 **Robust Processing**: Handles edge cases and provides detailed logging

## Supported Documentation Formats

1. **Sphinx Documentation** (Highest Priority)
   - Automatic detection of `conf.py` and `index.rst`
   - Support for Makefile-based builds
   - Fallback to direct Sphinx building

2. **Jupyter Notebooks**
   - Recursive search for `.ipynb` files
   - Conversion to markdown using `jupytext`
   - Integration with other documentation sources

3. **Python Docstrings**
   - AST-based extraction of module, class, and function docstrings
   - Structured markdown output with proper headers

4. **Raw Source Code**
   - Fallback for projects without structured documentation
   - Preserves code formatting and structure

## Installation

Install ContextMaker from PyPI:

```bash
python3 -m venv context_env
source context_env/bin/activate
pip install contextmaker
```

## Usage

### From the Command Line

ContextMaker automatically finds libraries on your system and generates complete documentation with function signatures and docstrings.

```bash
# Convert a library's documentation (automatic search)
contextmaker library_name

# Example: convert pixell documentation
contextmaker pixell

# Example: convert numpy documentation
contextmaker numpy
```

#### Advanced Usage

```bash
# Specify custom output path
contextmaker pixell --output ~/Documents/my_docs

# Specify manual input path (overrides automatic search)
contextmaker pixell --input_path /path/to/library/source

# Choose output format (txt or md)
contextmaker pixell --extension md

# Save directly to specified file without creating folders (rough mode)
contextmaker pixell --output ./pixell_context.txt --rough
```

#### Output

- **Default location:** `~/your_context_library/library_name.txt`
- **Content:** Complete documentation with function signatures, docstrings, examples, and API references
- **Format:** Clean text optimized for AI agent ingestion

---

### From a Python Script

You can also use ContextMaker programmatically in your Python scripts:

```python
import contextmaker

# Minimal usage (automatic search, default output path)
contextmaker.make("pixell")

# With custom output path
contextmaker.make("pixell", output_path="/tmp")

# With manual input path
contextmaker.make("pixell", input_path="/path/to/pixell/source")

# Choose output format (txt or md)
contextmaker.make("pixell", extension="md")

# Save directly to specified file without creating folders (rough mode)
contextmaker.make("pixell", output_path="./pixell_context.txt", rough=True)
```

## Examples

### Processing a Sphinx Project
```bash
contextmaker my_library --input_path /path/to/sphinx/docs
```

### Processing Notebooks Only
```bash
contextmaker tutorial_project --input_path /path/to/notebooks
```

### Custom Output Format
```bash
contextmaker numpy --extension md --output ~/my_docs
```

## Running the Jupyter Notebook

To launch and use the notebooks provided in this project, follow these steps:

1. **Install Jupyter**  
If Jupyter is not already installed, you can install it with:
```bash
pip install jupyter
```

2. **Launch Jupyter Notebook**  
Navigate to the project directory and run:
```bash
jupyter notebook
```
This will open the Jupyter interface in your web browser.

## Dependencies

- **Core**: Python 3.8+
- **Documentation**: Sphinx, jupytext, sphinx-rtd-theme
- **Processing**: markdownify, beautifulsoup4, html2text
- **Utilities**: rich, numpy, docutils, jinja2

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project uses the [CAMB](https://camb.info/) code developed by Antony Lewis and collaborators. Please see the CAMB website and documentation for more information.