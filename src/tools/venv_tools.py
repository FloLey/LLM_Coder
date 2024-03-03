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


class InstallRequirementsInput(BaseModel):
    python_path: str = Field(description="The path to the python executable in the venv")
    requirements_file: str = Field(description="path to the requirements.txt file to install requirements")


def install_requirements_in_env(python_path: str, requirements_file: str) -> str:
    """Installs requirements in the specified virtual environment from a requirements file."""
    try:
        # Execute the pip install command
        subprocess.run([python_path, "-m", "pip", "install", "-r", requirements_file], check=True)
        return f"Requirements installed in virtual environment with: {python_path} from {requirements_file}"
    except Exception as e:
        raise ToolException(f"Failed to install requirements: {str(e)}")


install_requirements_tool = StructuredTool.from_function(
    func=install_requirements_in_env,
    name="InstallRequirementsInEnv",
    description="Installs requirements in the specified virtual environment from a requirements file.",
    args_schema=InstallRequirementsInput,
    handle_tool_error=True
)


class CreateRequirementsInput(BaseModel):
    project_path: str = Field(description="The path to the project folder where the requirements.txt will be created")
    requirements: list[str] = Field(description="A list of package requirements to include in the requirements.txt file")

def create_requirements_file(project_path: str, requirements: list[str]) -> str:
    """Creates a requirements.txt file at the specified project path with the given requirements."""
    try:
        requirements_path = os.path.join(project_path, "requirements.txt")
        with open(requirements_path, 'w') as f:
            for requirement in requirements:
                f.write(f"{requirement}\n")
        return f"Created requirements.txt at {requirements_path}"
    except Exception as e:
        raise ToolException(f"Failed to create requirements.txt: {str(e)}")

create_requirements_file_tool = StructuredTool.from_function(
    func=create_requirements_file,
    name="CreateRequirementsFile",
    description="Creates a requirements.txt file in the specified project folder based on a list of requirements.",
    args_schema=CreateRequirementsInput,
    handle_tool_error=True
)