# ContextMaker

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

**Feature to enrich the CMBAgents:** Multi-Agent System for Science, Made by Cosmologists, Powered by [AG2](https://github.com/ag2ai/ag2).

## Acknowledgments

This project uses the [CAMB](https://camb.info/) code developed by Antony Lewis and collaborators. Please see the CAMB website and documentation for more information.

---

## Strategy

ContextMaker is designed to convert any scientific or software library documentation into a clean, standardized text format optimized for ingestion by CMBAgent.
It handles multiple input formats including Sphinx documentation, Markdown files, Jupyter notebooks, and source code with embedded docstrings.
When documentation is missing, ContextMaker can auto-generate basic API docs directly from the source code.
This makes it a versatile tool to prepare heterogeneous documentation sources into a consistent knowledge base for AI agents specialized in scientific research.

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/chadiaitekioui/contextmaker
cd contextmaker
python3 -m venv contextmaker_env
source contextmaker_env/bin/activate
pip install -e .
```

You can now use ContextMaker from the command line.

---

## Usage

### Simple Command Line Interface

ContextMaker automatically finds libraries on your system and generates complete documentation with function signatures and docstrings.

```bash
# Convert a library's documentation (automatic search)
contextmaker library_name

# Example: convert pixell documentation
contextmaker pixell

# Example: convert numpy documentation
contextmaker numpy
```

### Advanced Usage

```bash
# Specify custom output path
contextmaker pixell --output ~/Documents/my_docs

# Specify manual input path (overrides automatic search)
contextmaker pixell --input_path /path/to/library/source
```

### Output

- **Default location:** `~/your_context_library/library_name.txt`
- **Content:** Complete documentation with function signatures, docstrings, examples, and API references
- **Format:** Clean text optimized for AI agent ingestion

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

## Advanced Usage for Developers

### Direct Module Usage

```bash
# Use the module directly
python -m contextmaker.contextmaker pixell
```

### Manual Sphinx Conversion

For advanced users, you can use the markdown builder directly:

```bash
python src/contextmaker/converters/markdown_builder.py \
  --sphinx-source /path/to/docs \
  --output /path/to/output.txt \
  --source-root /path/to/source \
  --html-to-text
```

---

## Examples

### Convert pixell documentation

```bash
# 1. Clone pixell (if not already done)
git clone https://github.com/simonsobs/pixell.git ~/Documents/GitHub/pixell

# 2. Generate documentation
contextmaker pixell

# 3. Result: ~/your_context_library/pixell.txt
```

### Convert numpy documentation

```bash
# 1. Clone numpy
git clone https://github.com/numpy/numpy.git ~/Documents/GitHub/numpy

# 2. Generate documentation
contextmaker numpy

# 3. Result: ~/your_context_library/numpy.txt
```

---

## Troubleshooting

### Command not found
```bash
# Reinstall the package
pip install -e .

# Use module directly
python -m contextmaker.contextmaker pixell
```

### Library not found
```bash
# Use manual path
contextmaker pixell --input_path /path/to/pixell/repo
```

### No documentation detected
- Ensure the library has a `docs/` or `doc/` directory with `conf.py` and `index.rst`
- Clone the official repository if using an installed package
