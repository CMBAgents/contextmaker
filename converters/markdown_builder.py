#!/usr/bin/env python
"""
This script builds Sphinx documentation in Markdown format and combines it into a single file
for use as context with Large Language Models (LLMs).

It can be used:
1. As a pre-build step in ReadTheDocs
2. Locally to generate markdown documentation
3. In CI/CD pipelines

Usage:
    python markdown_builder.py [--exclude file1,file2,...] [--output output_file] [--no-install]

Options:
    --exclude: Comma-separated list of files to exclude (without .md extension)
    --output: Output file path
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build Sphinx documentation in Markdown format for LLM context.")
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-separated list of files to exclude (without .md extension)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output file path",
    )
    parser.add_argument(
        "--sphinx-source",
        type=str,
        required=True,
        help="Path to Sphinx source directory (where conf.py and index.rst are)",
    )
    parser.add_argument(
        "--conf",
        type=str,
        help="Path to conf.py (default: <sphinx-source>/conf.py)",
    )
    parser.add_argument(
        "--index",
        type=str,
        help="Path to index.rst (default: <sphinx-source>/index.rst)",
    )
    parser.add_argument(
        "--notebook",
        type=str,
        default=None,
        help="Path to notebook to convert and append",
    )
    return parser.parse_args()


def build_markdown(sphinx_source, conf_path):
    build_dir = tempfile.mkdtemp(prefix="sphinx_build_")
    print(f" 📚 build_dir: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)

    # Create a temporary conf.py disabling intersphinx to avoid markdown build errors
    temp_conf_dir = os.path.join(build_dir, "temp_conf")
    os.makedirs(temp_conf_dir, exist_ok=True)
    temp_conf_path = os.path.join(temp_conf_dir, "conf.py")

    with open(conf_path, encoding="utf-8") as f:
        conf = f.read()

    # Simple fix: remove intersphinx extension if present
    conf = conf.replace("'sphinx.ext.intersphinx',", "")

    with open(temp_conf_path, "w", encoding="utf-8") as f:
        f.write(conf)

    # Debug prints
    print(f"sphinx_source: {sphinx_source}")
    print(f"conf_path: {conf_path}")
    print(f"build_dir: {build_dir}")
    print(f"sphinx-build command: sphinx-build -b markdown -c {temp_conf_dir} {sphinx_source} {build_dir}")

    print("Running sphinx-build...")
    result = subprocess.run(
        [
            "sphinx-build",
            "-b",
            "markdown",
            "-c",
            temp_conf_dir,
            sphinx_source,
            build_dir,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f" ❌ Warning: sphinx-build failed with return code {result.returncode}")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)

    # List files in build_dir after sphinx-build
    print("Files in build_dir after sphinx-build:", os.listdir(build_dir))

    shutil.rmtree(temp_conf_dir)
    return build_dir


def extract_toctree_order(index_path):
    try:
        with open(index_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Could not read {index_path}: {e}")
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

    return toctree_docs


def combine_markdown(build_dir, exclude, output, index_path):
    md_files = glob.glob(os.path.join(build_dir, "*.md"))
    exclude_set = set(f"{e.strip()}.md" for e in exclude if e.strip())

    # Filter files
    filtered = [f for f in md_files if os.path.basename(f) not in exclude_set]

    # Separate index.md and others
    index_md = None
    others = []
    for f in filtered:
        if os.path.basename(f).lower() == "index.md":
            index_md = f
        else:
            others.append(f)

    # Order others by toctree order if possible
    toctree_order = extract_toctree_order(index_path) if index_path else []
    name_to_file = {os.path.splitext(os.path.basename(f))[0]: f for f in others}
    ordered = []
    for doc in toctree_order:
        if doc in name_to_file:
            ordered.append(name_to_file.pop(doc))
    # Append any files not in toctree (alphabetical)
    remaining = sorted(name_to_file.values())
    ordered.extend(remaining)

    final_order = ([index_md] if index_md else []) + ordered

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as out:
        out.write("# Combined Documentation\n\n---\n\n")
        for f in final_order:
            section = os.path.splitext(os.path.basename(f))[0]
            out.write(f"## {section}\n\n")
            with open(f, encoding="utf-8") as infile:
                out.write(infile.read())
                out.write("\n\n")
    print(f"Combined markdown written to {output}")


def convert_notebook(nb_path):
    import shutil

    if not shutil.which("jupytext"):
        print("Error: jupytext is required to convert notebooks.")
        return None

    md_path = os.path.splitext(nb_path)[0] + ".md"
    cmd = ["jupytext", "--to", "md", "--opt", "notebook_metadata_filter=-all", nb_path]
    print(f"Converting notebook {nb_path} to markdown...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to convert notebook:\n{result.stderr}")
        return None
    if not os.path.exists(md_path):
        print(f"Expected markdown file {md_path} not found after conversion.")
        return None
    return md_path


def append_notebook_markdown(output_file, notebook_md):
    with open(output_file, "a", encoding="utf-8") as out, open(notebook_md, encoding="utf-8") as nb_md:
        out.write("\n\n# Notebook\n\n---\n\n")
        out.write(nb_md.read())
    print(f"Appended notebook markdown from {notebook_md} to {output_file}")


def main():
    args = parse_args()

    exclude = args.exclude.split(",") if args.exclude else []

    sphinx_source = os.path.abspath(args.sphinx_source)
    conf_path = os.path.abspath(args.conf) if args.conf else os.path.join(sphinx_source, "conf.py")
    index_path = os.path.abspath(args.index) if args.index else os.path.join(sphinx_source, "index.rst")

    build_dir = build_markdown(sphinx_source, conf_path)
    combine_markdown(build_dir, exclude, args.output, index_path)

    if args.notebook:
        notebook_md = convert_notebook(args.notebook)
        if notebook_md:
            append_notebook_markdown(args.output, notebook_md)

    if __name__ == "__main__":
        sys.exit(main())