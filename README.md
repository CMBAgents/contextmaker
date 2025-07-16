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
python3 -m venv context_env
source context_env/bin/activate
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
contextmaker.make("pixell")

# With custom output path
contextmaker.make("pixell", output_path="/tmp")

# With manual input path
contextmaker.make("pixell", input_path="/path/to/pixell/source")

# Example: choose output format (txt or md)
contextmaker.make("pixell", extension="md")

# CLI usage with extension
contextmaker pixell --extension md
```