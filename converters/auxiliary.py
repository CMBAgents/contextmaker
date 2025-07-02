def find_format(lib_path):
    """
    Find the format of a library.
    """
    if has_documentation(lib_path):
        return 'sphinx'
    elif has_notebook(lib_path):
        return 'notebook'
    elif has_source(lib_path):
        return 'source'
    elif has_markdown(lib_path):
        return 'markdown'
    else:
        raise ValueError("The library is not a valid documentation library")

def has_documentation(lib_path):
    return True

def has_notebook(lib_path):
    return True

def has_source(lib_path):
    return True

def has_markdown(lib_path):
    return True

def convert_markdown_to_txt(file_path):
    """
    Convert a Markdown file to a txt file.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    return content

