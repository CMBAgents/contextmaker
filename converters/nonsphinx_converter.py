import jupytext
import pdoc
from converters import auxiliary

def combine_markdown_files(lib_path, output_path):
    """
    Combine the markdown files into a single file.
    """
    #TODO : combine the markdown files into a single file
    pass

def create_markdown_files(lib_path, output_path):
    """
    Create markdown files from the library.
    """
    if auxiliary.has_notebook(lib_path):
        #TODO : convert the notebook to markdown
        jupytext.convert(lib_path, output_path)
    elif auxiliary.has_docstrings(lib_path):
        #TODO : convert the docstrings to markdown
        pdoc.convert(lib_path, output_path)
    elif auxiliary.has_source(lib_path):
        #TODO : convert the source code to txt directly
        pass
    else:
        raise ValueError("The library is not a valid documentation library")
    return None