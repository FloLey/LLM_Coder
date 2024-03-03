from langchain_core.pydantic_v1 import BaseModel, Field
import subprocess

from langchain_core.tools import ToolException, StructuredTool


class TestDirectoryInput(BaseModel):
    test_dir: str = Field(description="The directory containing tests to run with pytest")
    venv_python_path: str = Field(description="The path to the Python executable inside the venv")


def run_pytest_in_directory(test_dir: str, venv_python_path: str) -> str:
    """Runs pytest on all tests in the specified directory within a specified venv, returning detailed output."""
    python_executable = venv_python_path
    pytest_command = [python_executable, "-m", "pytest", test_dir]

    try:
        result = subprocess.run(pytest_command, capture_output=True, text=True, check=True)
        output = result.stdout + "\n" + result.stderr
        return f"Tests executed successfully:\n{output}"
    except subprocess.CalledProcessError as e:
        # This captures errors from the subprocess itself and includes full output (stdout + stderr)
        full_output = e.stdout + "\n" + e.stderr
        raise ToolException(f"Failed to run tests with detailed output:\n{pytest_command}\n{full_output}\n")
    except Exception as e:
        # This captures any other exceptions, e.g., if the subprocess call fails to execute
        raise ToolException(f"Failed to run tests: \n{pytest_command}\n{str(e)}")


run_pytest_tool = StructuredTool.from_function(
    func=run_pytest_in_directory,
    name="RunPytest",
    description="Runs pytest on all tests in the specified directory within a specified venv.",
    args_schema=TestDirectoryInput,
    handle_tool_error=True
)
