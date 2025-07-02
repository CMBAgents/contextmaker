from converters import auxiliary, markdown_builder

#TODO: treat the 3 cases : source code, jupyter notebooks, sphinx documentation
#TODO: reflechir a la gestion des acces a source et les path en general

def convert_sphinx_docs_to_txt(input_path, output_path):
    """
    Convert Sphinx documentation to txt format.
    """
    # Convert the sphinx documentation to a txt file
    markdown_builder.main()
    # Convert the markdown file to a txt file
    final_txt = auxiliary.convert_markdown_to_txt(input_path, output_path)
    # Print the result
    print(f"Converting Sphinx documentation from {input_path} to {output_path} into a markdown file")
    return final_txt