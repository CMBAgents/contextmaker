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
    else:
        raise ValueError("The library is not a valid documentation library")

def has_documentation(lib_path):
    return True

def has_notebook(lib_path):
    return True

def has_source(lib_path):
    return True

def convert_markdown_to_txt(file_path, output_path):
    """
    Convert a Markdown file to a txt file by copying its contents as-is.
    """
    print(f"Converting markdown from {file_path} to {output_path}")
    with open(file_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()
    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(content)
    return None