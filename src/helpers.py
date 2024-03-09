import os


def read_files_in_directory_as_string(directory_path):
    result_string = ""
    # Walk through all files and directories within the given directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if not file.endswith('.pyc'):  # Skip .pyc files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        # Read the content and replace curly brackets with double curly brackets
                        content = file.read().replace('{', '{{').replace('}', '}}')
                        # Append file path and content to the result string
                        result_string += f"File: {file_path}\nContent:\n{content}\n\n"
                except Exception as e:
                    # Handle cases where the file cannot be read
                    result_string += f"Error reading {file_path}: {e}\n\n"
    return result_string