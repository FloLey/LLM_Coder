import os
import shutil
from typing import Optional

from langchain_core.tools import StructuredTool, ToolException
from pydantic.v1 import BaseModel, Field


class FilePathInput(BaseModel):
    path: str = Field(description="The path of the file on which an action will be applied.")


class FileCreationInput(FilePathInput):
    content: Optional[str] = Field(default="", description="The content to write into the file. optional")

class DirectoryPathInput(BaseModel):
    path: str = Field(description="The path of the directory to create.")


def create_directory(path: str) -> str:
    """
    Creates a directory at the specified path. Cannot create files
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)

        os.makedirs(path)
        return f"Directory created at: {path}"
    except Exception as e:
        raise Exception(f"Failed to create directory: {str(e)}")


create_directory_tool = StructuredTool.from_function(
    func=create_directory,
    name="CreateDirectory",
    description="Creates a directory at the specified path. Cannot create files",
    args_schema=DirectoryPathInput,
    handle_tool_error=True
)


def create_file_with_content(path: str, content: str = "") -> str:
    """Creates a file at the specified path and writes the provided content to it."""
    try:
        with open(path, 'w') as file:
            file.write(content)
        return f"File created with content {content} at: {path}"
    except Exception as e:
        raise ToolException(f"Failed to create file with content: {str(e)}")


create_file_tool = StructuredTool.from_function(
    func=create_file_with_content,
    name="CreateFile",
    description="Creates a file at the specified path and writes the provided content to it if any.",
    args_schema=FileCreationInput,
    handle_tool_error=True
)

def read_file_content(path: str) -> str:
    """Reads and returns the content of the file at the specified path."""
    try:
        with open(path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        raise ToolException(f"Failed to read file content: {str(e)}")


read_file_content_tool = StructuredTool.from_function(
    func=read_file_content,
    name="ReadFileContent",
    description="Reads and returns the content of the file at the specified path.",
    args_schema=FilePathInput,
    handle_tool_error=True
)


def update_file_content(path: str, content: str) -> str:
    """
    Updates the content of the file at the specified path with new content.
    """
    try:
        with open(path, 'w') as file:
            file.write(content)
        return f"File content updated at: {path}"
    except Exception as e:
        raise ToolException(f"Failed to update file content: {str(e)}")


update_file_content_tool = StructuredTool.from_function(
    func=update_file_content,
    name="UpdateFileContent",
    description="Updates the content of the file at the specified path with new content.",
    args_schema=FileCreationInput,
    handle_tool_error=True
)
