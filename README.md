# ContextMaker (Work in Progress - Does not work yet)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

**Feature to enrich the CMBAgents:** Multi-Agent System for Science, Made by Cosmologists, Powered by [AG2](https://github.com/ag2ai/ag2).
#
# Acknowledgments

This project uses the [CAMB](https://camb.info/) code developed by Antony Lewis and collaborators. Please see the CAMB website and documentation for more information.

---

## Strategy

Context_Maker is designed to convert any scientific or software library documentation into a clean, standardized text format optimized for ingestion by CMBAgent.
It handles multiple input formats including Sphinx documentation, Markdown files, Jupyter notebooks, and source code with embedded docstrings.
When documentation is missing, Context\_Maker can auto-generate basic API docs directly from the source code.
This makes it a versatile tool to prepare heterogeneous documentation sources into a consistent knowledge base for AI agents specialized in scientific research.

---

## Developer Setup

Clone the repository and install in editable mode:

```bash
git clone https://github.com/CMBAgents/Context_Maker
cd Context_Maker
python3 -m venv contextmaker_env
source contextmaker_env/bin/activate
pip install -e .
```

You can now open the source in your preferred IDE (VSCode, Emacs, etc.) for development.

---

## Usage

Once your virtual environment is activated and dependencies are installed, you can run **Context_Maker** from the command line or import it as a Python module.

### Command Line Interface (CLI)

```bash
# Convert a library's documentation folder into a CMBAgent-friendly text file
python -m context_maker.convert --input_path /path/to/library/docs --output_path ./converted_docs

# Example: convert Sphinx docs
python -m context_maker.convert --input_path ./my_library/docs --output_path ./my_library_converted

# Convert a repository root folder (will auto-detect docs or source)
python -m context_maker.convert --input_path ./my_library --output_path ./my_library_converted
```

---

### Python API

You can also use Context_Maker programmatically in your scripts:

```python
from context_maker import convert

input_path = "/path/to/library"
output_path = "./converted_docs"

# Convert docs, notebooks, or source code to clean text for CMBAgent
convert.run_conversion(input_path=input_path, output_path=output_path)
```

---

### Supported Inputs

* Sphinx documentation (conf.py + `.rst`)
* Markdown README files (`README.md`)
* Jupyter notebooks (`.ipynb`)
* Python source files with docstrings (auto-generated docs if no user docs)

---

### Output

* A plain text (`.txt`) file containing cleaned and normalized documentation, optimized for CMBAgent ingestion.

---

## Generate Markdown Documentation for Any Library

The `converters/markdown_builder.py` script allows you to generate Sphinx documentation of a Python library into a single Markdown file, usable as context for LLMs.

### Usage

```bash
python converters/markdown_builder.py \
  --sphinx-source /chemin/vers/monprojet/docs \
  --output /chemin/vers/output.md \
  --source-root /chemin/vers/monprojet/monprojet
```

- `--sphinx-source` : path to the directory containing `conf.py` and `index.rst` (typically the project's `docs` directory).
- `--output` : path to the output Markdown file.
- `--source-root` : absolute path to the root directory of the source code to document (typically the directory containing the main project package).

**Example for a project structured as follows:**
```
monprojet/
  monprojet/    # source code
  docs/         # Sphinx documentation (conf.py, index.rst)
```
The command will be:
```bash
python converters/markdown_builder.py \
  --sphinx-source monprojet/docs \
  --output output.md \
  --source-root monprojet/monprojet
```

The script automatically adds the source code path to PYTHONPATH during generation, which allows importing the package even if it's not installed.

---
