import os
import re

def process_templates(directory):
    """
    Automates the removal of specific code snippets and the replacement of a button in HTML or template files.

    Args:
        directory (str): Path to the templates directory to process.

    Returns:
        None
    """
    # Define the patterns to remove and replace
    script_pattern = r"<script src=\\\"\\{% static 'java/cours\\.js' %\\}\"></script>"
    iframe_block_pattern = r"<!-- Section pour afficher le PDF via iframe -->.*?<div id=\"resize-handle\".*?</div>"
    button_pattern = r"<button id=\\\"show-course-btn\\\".*?onclick=\\\".*?\\\">📚</button>"
    new_button = ("<button id=\\\"show-course-btn\\\" class=\\\"floating-btn\\\" type=\\\"button\\\" "
                  "onclick=\\\"window.open('https://drive.google.com/drive/folders/1Xd_FaJbPk4FJv3G5-96L7G0UlQnUZuSf', '_blank');\\\">📚</button>")

    modified_files = []

    print(f"Scanning directory: {directory}")

    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.html'):
                file_path = os.path.join(root, file_name)
                print(f"Processing file: {file_path}")

                # Read the file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()

                    # Apply the changes
                    new_content = re.sub(script_pattern, "", content)
                    new_content = re.sub(iframe_block_pattern, "", new_content, flags=re.DOTALL)
                    new_content = re.sub(button_pattern, new_button, new_content)

                    # Check if the content was modified
                    if content != new_content:
                        # Write the modified content back to the file
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(new_content)

                        modified_files.append(file_path)
                        print(f"Modified: {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Print the modified files
    if modified_files:
        print("Modified files:")
        for modified_file in modified_files:
            print(modified_file)
    else:
        print("No files were modified.")
