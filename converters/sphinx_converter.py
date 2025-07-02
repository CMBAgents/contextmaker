from camb.docs import markdown_builder
from converters import auxiliary

def convert_sphinx_docs_to_txt(input_path, output_path):
    """
    Convert Sphinx documentation to txt format.
    """
    # Convert the sphinx documentation to a markdown file
    markdown_builder.main()
    # Convert the markdown file to a txt file
    final_txt = auxiliary.convert_markdown_to_txt(output_path)
    # Print the result
    print(f"Converting Sphinx documentation from {input_path} to {output_path} into a markdown file")
    return final_txt