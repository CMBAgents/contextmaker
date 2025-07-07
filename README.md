# ContextMaker

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

**Feature to enrich the CMBAgents:** Multi-Agent System for Science, Made by Cosmologists, Powered by [AG2](https://github.com/ag2ai/ag2).

## Acknowledgments

This project uses the [CAMB](https://camb.info/) code developed by Antony Lewis and collaborators. Please see the CAMB website and documentation for more information.

---

## Installation

Install ContextMaker from PyPI:

```bash
pip install contextmaker
```

---

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
contextmaker.convert("pixell")

# With custom output path
contextmaker.convert("pixell", output_path="/tmp")

# With manual input path
contextmaker.convert("pixell", input_path="/path/to/pixell/source")
```

This will generate a text file with the complete documentation, just like the CLI.

---

### Supported Inputs

* Sphinx documentation (conf.py + `.rst`) - **Complete documentation with signatures**
* Markdown README files (`README.md`)
* Jupyter notebooks (`.ipynb`)
* Python source files with docstrings (auto-generated docs if no user docs)

---

### Library Requirements

For complete documentation extraction, the library should have:
- A `docs/` or `doc/` directory containing `conf.py` and `index.rst`
- Source code accessible for docstring extraction

If only the installed package is found (without Sphinx docs), ContextMaker will extract available docstrings from the source code.

---

## Troubleshooting

### Library not found
```bash
# Use manual path
contextmaker pixell --input_path /path/to/pixell/repo
```

### No documentation detected
- Ensure the library has a `docs/` or `doc/` directory with `conf.py` and `index.rst`
- Clone the official repository if using an installed package