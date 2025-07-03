import os

def find_format(lib_path):
    """
    Find the format of a library.
    """
    if has_documentation(lib_path):
        return 'sphinx'
    elif has_notebook(lib_path):
        return 'notebook'
    elif has_docstrings(lib_path):
        return 'docstrings'
    elif has_source(lib_path):
        return 'source'
    else:
        raise ValueError("The library is not a valid documentation library")

def has_documentation(lib_path):
    """
    Check if the library has documentation (including notebooks)
    """
    # Check if the library has a documentation folder (contains conf.py and index.rst)
    if os.path.exists(os.path.join(lib_path, 'docs')):
        if os.path.exists(os.path.join(lib_path, 'docs', 'conf.py')) and os.path.exists(os.path.join(lib_path, 'docs', 'index.rst')):
            return True
    return False

def has_notebook(lib_path):
    """
    Check if the library has a notebook and no documentation.
    """
    # Check if the library has a notebook folder (contains a .ipynb file)
    if not has_documentation(lib_path):
        if os.path.exists(os.path.join(lib_path, 'notebooks')):
            if os.path.exists(os.path.join(lib_path, 'notebooks', '*.ipynb')):
                return True
    return False

def has_docstrings(lib_path):
    """
    Check if the library has docstrings.
    """
    if not has_documentation(lib_path) :
        #TODO : check if the library has docstrings
        pass
    return False

def has_source(lib_path):
    """
    Check if the library has source code.
    """
    if not has_documentation(lib_path):
        if not has_notebook(lib_path):
            if not has_docstrings(lib_path):
                return True
    return False
"""
def convert_markdown_to_txt(output_path):
    
    Convert a Markdown file to a txt file by copying its contents as-is.
    
    print(f"Converting markdown from {output_path}")
    with open(output_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()
    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(content)
    return None
"""