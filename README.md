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

---

## 🚀 Advanced Features

### Intelligent Sphinx Documentation Detection

ContextMaker automatically detects and uses the most efficient method for building Sphinx documentation:

#### 1. **Sphinx Makefile (Highest Priority)**
- Automatically detects Sphinx Makefiles in your project
- Adds missing `text` targets for text output
- Uses `make text` for optimal build performance
- **Requires:** GNU Make installed on your system

#### 2. **Direct Sphinx Building (Smart Fallback)**
- Automatically falls back to direct `sphinx-build` calls when `make` is unavailable
- No manual intervention required
- Works on all systems with Sphinx installed
- **Requires:** Only Sphinx (`pip install sphinx`)

#### 3. **Standard Sphinx Processing**
- Traditional Sphinx documentation processing
- Handles complex configurations and custom themes
- **Requires:** Sphinx installed

### Automatic Fallback System

ContextMaker intelligently handles system dependencies:

```bash
# If 'make' is available: Uses Makefile (fastest)
📋 Sphinx Makefile found and 'make' is available - using highest priority method

# If 'make' is not available: Automatically falls back to direct Sphinx
📋 Sphinx Makefile found but 'make' not available - will use direct Sphinx building

# If no Makefile: Uses standard Sphinx method
📚 Standard Sphinx documentation found
```

### System Requirements

- **Python 3.8+** (required)
- **Sphinx** (required for Sphinx projects)
- **GNU Make** (optional, for optimal performance)

#### Installing GNU Make (Optional)

**macOS:**
```bash
xcode-select --install
```

**Ubuntu/Debian:**
```bash
sudo apt-get install make
```

**RHEL/CentOS:**
```bash
sudo yum install make
```

**Windows:**
- Install MinGW, Cygwin, or use WSL
- Or let ContextMaker automatically use the Python fallback

---

## 📚 Supported Documentation Formats