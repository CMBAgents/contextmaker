#!/usr/bin/env python
"""
This script builds Sphinx documentation in Markdown format and combines it into a single file
for use as context with Large Language Models (LLMs).
"""

import argparse
import glob
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import html2text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Build Sphinx documentation in Markdown format for LLM context.")
    parser.add_argument("--exclude", type=str, default="", help="Comma-separated list of files to exclude (without .md extension)")
    parser.add_argument("--output", type=str, required=True, help="Output file path")
    parser.add_argument("--sphinx-source", type=str, required=True, help="Path to Sphinx source directory (where conf.py and index.rst are)")
    parser.add_argument("--conf", type=str, default=None, help="Path to conf.py (default: <sphinx-source>/conf.py)")
    parser.add_argument("--index", type=str, default=None, help="Path to index.rst (default: <sphinx-source>/index.rst)")
    parser.add_argument("--notebook", type=str, default=None, help="Path to notebook to convert and append")
    parser.add_argument("--source-root", type=str, required=True, help="Absolute path to the root of the source code to add to sys.path for Sphinx autodoc.")
    parser.add_argument("--library-name", type=str, default=None, help="Name of the library for the documentation title.")
    parser.add_argument("--html-to-text", action="store_true", help="Build Sphinx HTML and convert to text instead of Markdown.")
    return parser.parse_args()


def build_markdown(sphinx_source, conf_path, source_root):
    build_dir = tempfile.mkdtemp(prefix="sphinx_build_")
    logger.info(f" 📄 Temporary build directory: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)

    conf_dir = os.path.dirname(conf_path)

    logger.info(f" 📄 sphinx_source: {sphinx_source}")
    logger.info(f" 📄 conf_path: {conf_path}")
    logger.info(f" 📄 build_dir: {build_dir}")
    logger.info(f" 📄 sphinx-build command: sphinx-build -b markdown -c {conf_dir} {sphinx_source} {build_dir}")
    logger.info(" 📄 Running sphinx-build...")

    result = subprocess.run(
        ["sphinx-build", "-b", "markdown", "-c", conf_dir, sphinx_source, build_dir],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
    )

    if result.returncode != 0:
        logger.error(" 📄 sphinx-build failed with return code %s", result.returncode)
        logger.error(" 📄 stdout:\n%s", result.stdout)
        logger.error(" 📄 stderr:\n%s", result.stderr)
    else:
        logger.info(" ✅ sphinx-build completed successfully.")

    logger.info(" 📄 Files in build_dir after sphinx-build: %s", os.listdir(build_dir))

    return build_dir


def extract_toctree_order(index_path):
    try:
        with open(index_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f" 📄  Could not read {index_path}: {e}")
        return []

    toctree_docs = []
    in_toctree = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(".. toctree::"):
            in_toctree = True
            continue
        if in_toctree:
            if stripped == "" or stripped.startswith(":"):
                continue
            if stripped.startswith(".. "):  # another directive
                break
            toctree_docs.append(stripped)

    logger.debug(f"Extracted toctree documents: {toctree_docs}")
    return toctree_docs


def combine_markdown(build_dir, exclude, output, index_path, library_name):
    md_files = glob.glob(os.path.join(build_dir, "*.md"))
    exclude_set = set(f"{e.strip()}.md" for e in exclude if e.strip())

    filtered = [f for f in md_files if os.path.basename(f) not in exclude_set]

    index_md = None
    others = []
    for f in filtered:
        if os.path.basename(f).lower() == "index.md":
            index_md = f
        else:
            others.append(f)

    toctree_order = extract_toctree_order(index_path) if index_path else []
    name_to_file = {os.path.splitext(os.path.basename(f))[0]: f for f in others}
    ordered = []
    for doc in toctree_order:
        if doc in name_to_file:
            ordered.append(name_to_file.pop(doc))

    remaining = sorted(name_to_file.values())
    ordered.extend(remaining)

    final_order = ([index_md] if index_md else []) + ordered

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as out:
        out.write(f"# - {library_name} | Complete Documentation -\n\n")
        for i, f in enumerate(final_order):
            if i > 0:
                out.write("\n\n---\n\n")
            section = os.path.splitext(os.path.basename(f))[0]
            out.write(f"## {section}\n\n")
            with open(f, encoding="utf-8") as infile:
                out.write(infile.read())
                out.write("\n\n")

    logger.info(f" 📄 Combined markdown written to {output}")


def convert_notebook(nb_path):
    if not shutil.which("jupytext"):
        logger.error(" 📄 jupytext is required to convert notebooks.")
        return None

    md_path = os.path.splitext(nb_path)[0] + ".md"
    cmd = ["jupytext", "--to", "md", "--opt", "notebook_metadata_filter=-all", nb_path]
    logger.info(f" 📄 Converting notebook {nb_path} to markdown...")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f" 📄 Failed to convert notebook:\n{result.stderr}")
        return None
    if not os.path.exists(md_path):
        logger.error(f" 📄 Expected markdown file {md_path} not found after conversion.")
        return None

    logger.info(f" ✅ Notebook converted to {md_path}")
    return md_path


def append_notebook_markdown(output_file, notebook_md):
    with open(output_file, "a", encoding="utf-8") as out, open(notebook_md, encoding="utf-8") as nb_md:
        out.write("\n\n# Notebook\n\n---\n\n")
        out.write(nb_md.read())
    logger.info(f" 📄 Appended notebook markdown from {notebook_md} to {output_file}")


def build_html_and_convert_to_text(sphinx_source, conf_path, source_root, output):
    build_dir = tempfile.mkdtemp(prefix="sphinx_html_build_")
    logger.info(f" 📄 Temporary HTML build directory: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)
    conf_dir = os.path.dirname(conf_path)

    logger.info(f" 📄 sphinx_source: {sphinx_source}")
    logger.info(f" 📄 conf_path: {conf_path}")
    logger.info(f" 📄 build_dir: {build_dir}")
    logger.info(f" 📄 sphinx-build command: sphinx-build -b html -c {conf_dir} {sphinx_source} {build_dir}")
    logger.info(" 📄 Running sphinx-build (HTML)...")

    result = subprocess.run(
        ["sphinx-build", "-b", "html", "-c", conf_dir, sphinx_source, build_dir],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": source_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
    )

    if result.returncode != 0:
        logger.error(" 📄 sphinx-build (HTML) failed with return code %s", result.returncode)
        logger.error(" 📄 stdout:\n%s", result.stdout)
        logger.error(" 📄 stderr:\n%s", result.stderr)
        
        # Check for common error patterns and provide helpful messages
        stderr_lower = result.stderr.lower()
        if "circular import" in stderr_lower or "partially initialized module" in stderr_lower:
            logger.error(" 📄 This appears to be a circular import issue. This is common with complex libraries like numpy.")
            logger.error(" 📄 The library may need to be properly installed or the documentation may have dependency issues.")
        elif "import error" in stderr_lower:
            logger.error(" 📄 Import error detected. The library may have missing dependencies for documentation building.")
        
        return False
    else:
        logger.info(" ✅ sphinx-build (HTML) completed successfully.")

    logger.info(" 📄 Files in build_dir after sphinx-build (HTML): %s", os.listdir(build_dir))

    # Convert all HTML files to text and concatenate
    html_files = sorted(glob.glob(os.path.join(build_dir, "*.html")))
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # Extract library name from output path
    library_name = os.path.splitext(os.path.basename(output))[0]
    
    with open(output, "w", encoding="utf-8") as out:
        out.write(f"# - Complete Documentation | {library_name} -\n\n")
        for html_file in html_files:
            section = os.path.splitext(os.path.basename(html_file))[0]
            out.write(f"## {section}\n\n")
            with open(html_file, "r", encoding="utf-8") as f:
                html = f.read()
            text = html2text.html2text(html)
            out.write(text)
            out.write("\n\n---\n\n")
    logger.info(f" 📄 Combined HTML-to-text written to {output}")
    return True


def main():
    args = parse_args()

    exclude = args.exclude.split(",") if args.exclude else []

    sphinx_source = os.path.abspath(args.sphinx_source)
    conf_path = os.path.abspath(args.conf) if args.conf else os.path.join(sphinx_source, "conf.py")
    index_path = os.path.abspath(args.index) if args.index else os.path.join(sphinx_source, "index.rst")
    source_root = os.path.abspath(args.source_root)
    
    library_name = args.library_name if args.library_name else os.path.basename(source_root)

    # Nouveau mode : HTML -> texte
    if hasattr(args, 'html_to_text') and args.html_to_text:
        build_html_and_convert_to_text(sphinx_source, conf_path, source_root, args.output)
        logger.info(" ✅ Sphinx HTML to text conversion successful.")
        return

    build_dir = build_markdown(sphinx_source, conf_path, source_root)
    combine_markdown(build_dir, exclude, args.output, index_path, library_name)

    if args.notebook:
        notebook_md = convert_notebook(args.notebook)
        if notebook_md:
            append_notebook_markdown(args.output, notebook_md)

    logger.info(" ✅ Sphinx to Markdown conversion successful.")


if __name__ == "__main__":
    sys.exit(main())