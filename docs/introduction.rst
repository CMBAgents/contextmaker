Introduction
============

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/Python-3.8%2B-blue
   :target: https://python.org
   :alt: Python

**Feature to enrich the CMBAgents:** Multi-Agent System for Science, Made by Cosmologists, Powered by `AG2 <https://github.com/ag2ai/ag2>`_.

What is ContextMaker?
---------------------

ContextMaker is a powerful tool designed to make any scientific or software library documentation into a clean, standardized text format optimized for ingestion by CMBAgent. It handles multiple input formats including:

* **Sphinx documentation** (conf.py + .rst files)
* **Markdown files** (README.md, etc.)
* **Jupyter notebooks** (.ipynb)
* **Python source code** with embedded docstrings

When documentation is missing, ContextMaker can auto-generate basic API docs directly from the source code. This makes it a versatile tool to prepare heterogeneous documentation sources into a consistent knowledge base for AI agents specialized in scientific research.

Key Features
-----------

* **Multi-format Support**: Handles Sphinx, Markdown, Jupyter notebooks, and Python source code
* **Auto-documentation**: Generates API docs from source code when documentation is missing
* **Clean Output**: Produces standardized text format optimized for LLM ingestion
* **Flexible Input**: Works with both individual files and entire project directories
* **Scientific Focus**: Designed specifically for scientific and research libraries

Use Cases
---------

* **CMBAgent Integration**: Prepare documentation for ingestion by CMBAgent
* **Research Libraries**: Convert scientific library documentation to LLM-friendly format
* **Legacy Documentation**: Modernize old documentation formats
* **API Documentation**: Generate comprehensive API docs from source code
* **Knowledge Base Creation**: Build consistent documentation databases

Acknowledgments
--------------

This project uses the `CAMB <https://camb.info/>`_ code developed by Antony Lewis and collaborators. Please see the CAMB website and documentation for more information.

Quick Start
----------

.. code-block:: bash

   # Install ContextMaker
   git clone https://github.com/CMBAgents/Context_Maker
   cd Context_Maker
   python3 -m venv contextmaker_env
   source contextmaker_env/bin/activate
   pip install -e .

   # Convert documentation
   python -m contextmaker.contextmaker --input_path /path/to/library --output_path ./converted_docs 