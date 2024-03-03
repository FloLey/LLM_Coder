import os

from langchain_core.pydantic_v1 import BaseModel, Field
import subprocess

from langchain_core.tools import ToolException, StructuredTool


class VirtualEnvInput(BaseModel):
    path: str = Field(description="The path where the virtual environment should be created.")


def create_virtual_env(path: str) -> str:
    """Creates a virtual environment at the specified path and returns the path to the python executable"""
    try:
        subprocess.run([f"python", "-m", "venv", path], check=True)
        python_path = os.path.join(path, "bin", "python")
        return f"Created virtual environment with python executable path at {python_path}"
    except Exception as e:
        raise ToolException(f"Failed to create virtual environment: {str(e)}")


create_virtual_env_tool = StructuredTool.from_function(
    func=create_virtual_env,
    name="CreateVirtualEnv",
    description="Creates a virtual environment at the specified path and returns the path to the python executable",
    args_schema=VirtualEnvInput,
    handle_tool_error=True
)