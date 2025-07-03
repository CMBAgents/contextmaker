from converters import auxiliary
import subprocess

#TODO: reflechir a la gestion des acces a source et les path en general
#TODO: agir depuis le input path (s'y placer)

def convert_sphinx_docs_to_txt(input_path, output_path):
    """
    Convert Sphinx documentation to markdown format.
    """
    # Convert the sphinx documentation to a markdown file
    output = "combined.md"

    result = subprocess.run(
        [
            "python", "converters/markdown_builder.py",
            "--output", output
        ],
        capture_output=True,
        text=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    # Convert the markdown file to a txt file
    #TODO : the output is where we search for the markdown file
    #final_txt = auxiliary.convert_markdown_to_txt(output_path)
    # Print the result
    #print(f"Converting Sphinx documentation from {input_path} to {output_path} into a markdown file")
    return "yes"