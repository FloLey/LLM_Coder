# mport os
# import platform
# import subprocess
# from os.path import exists
# from shutil import rmtree
#
# from langchain.pydantic_v1 import BaseModel, Field
# from langchain_core.tools import ToolException, StructuredTool
#
#
# class WorkingDirOutput(BaseModel):
#     path: str = Field(description="The path of the current working directory")
#
#
# def get_working_dir() -> str:
#     """Get the path of the current working dir."""
#     try:
#         return os.getcwd()
#     except Exception as e:
#         raise ToolException(str(e))
#
#
# get_working_dir_tool = StructuredTool.from_function(
#     func=get_working_dir,
#     name="GetWorkingDir",
#     description="Get the path of the current working directory",
#     return_schema=WorkingDirOutput,
#     handle_tool_error=True  # This will handle any ToolExceptions raised by the function
# )
#
#
# class DesktopPathOutput(BaseModel):
#     path: str = Field(description="The path to the desktop folder")
#
#
# def get_path_desktop() -> str:
#     """Get the path to the desktop folder."""
#     try:
#         user_profile = os.environ.get('USERPROFILE')
#         if not user_profile:
#             raise ToolException("USERPROFILE environment variable is not set.")
#         desktop_path = os.path.join(user_profile, 'Desktop')
#         return desktop_path
#     except Exception as e:
#         raise ToolException(str(e))
#
#
# get_path_desktop_tool = StructuredTool.from_function(
#     func=get_path_desktop,
#     name="GetPathDesktop",
#     description="Get the path to the desktop folder",
#     return_schema=DesktopPathOutput,
#     handle_tool_error=True  # This will handle any ToolExceptions raised by the function
# )
#
#
# class ChangeDirInput(BaseModel):
#     path: str = Field(description="The path to change the working directory to, will be created if it doesn't exist.")
#
#
# def change_working_dir(path: str) -> str:
#     """Change the current working directory to the given path, creating the path if it doesn't exist."""
#     try:
#         if not os.path.exists(path):
#             os.makedirs(path)
#         os.chdir(path)
#         return f"Changed working directory to: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to change working directory: {str(e)}")
#
#
# change_working_dir_tool = StructuredTool.from_function(
#     func=change_working_dir,
#     name="ChangeWorkingDir",
#     description="Change the current working directory to the given path, creating the path if it doesn't exist.",
#     args_schema=ChangeDirInput,
#     handle_tool_error=True  # This ensures that any ToolExceptions raised are handled gracefully
# )
#
#
# class DirectoryPathInput(BaseModel):
#     path: str = Field(description="The path of the directory to create.")
#
#
# def create_directory(path: str) -> str:
#     """Creates a directory at the specified path."""
#     try:
#         if not exists(path):
#             os.makedirs(path)
#             return f"Directory created at: {path}"
#         else:
#             return f"Directory already exists: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to create directory: {str(e)}")
#
#
# create_directory_tool = StructuredTool.from_function(
#     func=create_directory,
#     name="CreateDirectory",
#     description="Creates a directory at the specified path.",
#     args_schema=DirectoryPathInput,
#     handle_tool_error=True
# )
#
#
# class FilePathInput(BaseModel):
#     path: str = Field(description="The path of the file on which an action will be applied.")
#
#
# class FileCreationInput(FilePathInput):
#     content: str = Field(default="", description="The content to write into the file.")
#
#
# def create_file_with_content(path: str, content: str = "") -> str:
#     """Creates a file at the specified path and writes the provided content to it."""
#     try:
#         with open(path, 'w') as file:
#             file.write(content)
#         return f"File created with content at: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to create file with content: {str(e)}")
#
#
# create_file_tool = StructuredTool.from_function(
#     func=create_file_with_content,
#     name="CreateFile",
#     description="Creates a file at the specified path and writes the provided content to it.",
#     args_schema=FileCreationInput,
#     handle_tool_error=True
# )
#
#
# def delete_file(path: str) -> str:
#     """Deletes the file at the specified path."""
#     try:
#         if exists(path):
#             os.remove(path)
#             return f"File deleted: {path}"
#         else:
#             return f"File does not exist: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to delete file: {str(e)}")
#
#
# delete_file_tool = StructuredTool.from_function(
#     func=delete_file,
#     name="DeleteFile",
#     description="Deletes the file at the specified path.",
#     args_schema=FilePathInput,  # Reusing the FilePathInput schema
#     handle_tool_error=True
# )
#
#
# def delete_directory(path: str) -> str:
#     """Deletes the directory at the specified path."""
#     try:
#         if exists(path):
#             rmtree(path)
#             return f"Directory deleted: {path}"
#         else:
#             return f"Directory does not exist: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to delete directory: {str(e)}")
#
#
# delete_directory_tool = StructuredTool.from_function(
#     func=delete_directory,
#     name="DeleteDirectory",
#     description="Deletes the directory at the specified path.",
#     args_schema=DirectoryPathInput,  # Reusing the DirectoryPathInput schema
#     handle_tool_error=True
# )
#
#
# def read_file_content(path: str) -> str:
#     """Reads and returns the content of the file at the specified path."""
#     try:
#         with open(path, 'r') as file:
#             content = file.read()
#         return content
#     except Exception as e:
#         raise ToolException(f"Failed to read file content: {str(e)}")
#
#
# read_file_content_tool = StructuredTool.from_function(
#     func=read_file_content,
#     name="ReadFileContent",
#     description="Reads and returns the content of the file at the specified path.",
#     args_schema=FilePathInput,
#     handle_tool_error=True
# )
#
#
# class VirtualEnvInput(BaseModel):
#     path: str = Field(description="The path where the virtual environment should be created.")
#
#
# def create_virtual_env(path: str) -> str:
#     """Creates a virtual environment at the specified path."""
#     try:
#         subprocess.run([f"python", "-m", "venv", path], check=True)
#         return f"Virtual environment created at: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to create virtual environment: {str(e)}")
#
#
# create_virtual_env_tool = StructuredTool.from_function(
#     func=create_virtual_env,
#     name="CreateVirtualEnv",
#     description="Creates a virtual environment at the specified path.",
#     args_schema=VirtualEnvInput,
#     handle_tool_error=True
# )
#
#
# class InstallRequirementsInput(BaseModel):
#     env_path: str = Field(description="The path to the virtual environment where the requirements should be installed.")
#     requirements_file: str = Field(description="The path to the requirements file.")
#
#
# def install_requirements_in_env(env_path: str, requirements_file: str) -> str:
#     """Installs requirements in the specified virtual environment from a requirements file."""
#     try:
#         # Determine the correct path for the Python executable based on the operating system
#         if platform.system() == "Windows":
#             python_executable = os.path.join(env_path, "Scripts", "python.exe")
#         else:
#             python_executable = os.path.join(env_path, "bin", "python")
#
#         # Execute the pip install command
#         subprocess.run([python_executable, "-m", "pip", "install", "-r", requirements_file], check=True)
#         return f"Requirements installed in virtual environment at: {env_path} from {requirements_file}"
#     except Exception as e:
#         raise ToolException(f"Failed to install requirements: {str(e)}")
#
#
# install_requirements_tool = StructuredTool.from_function(
#     func=install_requirements_in_env,
#     name="InstallRequirementsInEnv",
#     description="Installs requirements in the specified virtual environment from a requirements file.",
#     args_schema=InstallRequirementsInput,
#     handle_tool_error=True
# )
#
#
# class TestDirectoryInput(BaseModel):
#     test_dir: str = Field(description="The directory containing tests to run with pytest")
#     venv_python_path: str = Field(description="The path to the Python executable inside the venv")
#
#
# def run_pytest_in_directory(test_dir: str, venv_python_path: str = "") -> str:
#     """Runs pytest on all tests in the specified directory within a specified venv, returning detailed output."""
#     python_executable = venv_python_path if venv_python_path else "python"
#     pytest_command = [python_executable, "-m", "pytest", test_dir]
#
#     try:
#         result = subprocess.run(pytest_command, capture_output=True, text=True, check=True)
#         output = result.stdout + "\n" + result.stderr
#         return f"Tests executed successfully:\n{output}"
#     except subprocess.CalledProcessError as e:
#         # This captures errors from the subprocess itself and includes full output (stdout + stderr)
#         full_output = e.stdout + "\n" + e.stderr
#         raise ToolException(f"Failed to run tests with detailed output:\n{pytest_command}\n{full_output}\n")
#     except Exception as e:
#         # This captures any other exceptions, e.g., if the subprocess call fails to execute
#         raise ToolException(f"Failed to run tests: \n{pytest_command}\n{str(e)}")
#
# run_pytest_tool = StructuredTool.from_function(
#     func=run_pytest_in_directory,
#     name="RunPytest",
#     description="Runs pytest on all tests in the specified directory within a specified venv.",
#     args_schema=TestDirectoryInput,
#     handle_tool_error=True
# )
# TOOLS = [get_working_dir_tool, get_path_desktop_tool, change_working_dir_tool, create_directory_tool, create_file_tool,
#          delete_file_tool, delete_directory_tool, read_file_content_tool, install_requirements_tool,
#          create_virtual_env_tool, run_pytest_tool]
# NO_TOOLS = [change_working_dir_tool]mport os
# import platform
# import subprocess
# from os.path import exists
# from shutil import rmtree
#
# from langchain.pydantic_v1 import BaseModel, Field
# from langchain_core.tools import ToolException, StructuredTool
#
#
# class WorkingDirOutput(BaseModel):
#     path: str = Field(description="The path of the current working directory")
#
#
# def get_working_dir() -> str:
#     """Get the path of the current working dir."""
#     try:
#         return os.getcwd()
#     except Exception as e:
#         raise ToolException(str(e))
#
#
# get_working_dir_tool = StructuredTool.from_function(
#     func=get_working_dir,
#     name="GetWorkingDir",
#     description="Get the path of the current working directory",
#     return_schema=WorkingDirOutput,
#     handle_tool_error=True  # This will handle any ToolExceptions raised by the function
# )
#
#
# class DesktopPathOutput(BaseModel):
#     path: str = Field(description="The path to the desktop folder")
#
#
# def get_path_desktop() -> str:
#     """Get the path to the desktop folder."""
#     try:
#         user_profile = os.environ.get('USERPROFILE')
#         if not user_profile:
#             raise ToolException("USERPROFILE environment variable is not set.")
#         desktop_path = os.path.join(user_profile, 'Desktop')
#         return desktop_path
#     except Exception as e:
#         raise ToolException(str(e))
#
#
# get_path_desktop_tool = StructuredTool.from_function(
#     func=get_path_desktop,
#     name="GetPathDesktop",
#     description="Get the path to the desktop folder",
#     return_schema=DesktopPathOutput,
#     handle_tool_error=True  # This will handle any ToolExceptions raised by the function
# )
#
#
# class ChangeDirInput(BaseModel):
#     path: str = Field(description="The path to change the working directory to, will be created if it doesn't exist.")
#
#
# def change_working_dir(path: str) -> str:
#     """Change the current working directory to the given path, creating the path if it doesn't exist."""
#     try:
#         if not os.path.exists(path):
#             os.makedirs(path)
#         os.chdir(path)
#         return f"Changed working directory to: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to change working directory: {str(e)}")
#
#
# change_working_dir_tool = StructuredTool.from_function(
#     func=change_working_dir,
#     name="ChangeWorkingDir",
#     description="Change the current working directory to the given path, creating the path if it doesn't exist.",
#     args_schema=ChangeDirInput,
#     handle_tool_error=True  # This ensures that any ToolExceptions raised are handled gracefully
# )
#
#
# class DirectoryPathInput(BaseModel):
#     path: str = Field(description="The path of the directory to create.")
#
#
# def create_directory(path: str) -> str:
#     """Creates a directory at the specified path."""
#     try:
#         if not exists(path):
#             os.makedirs(path)
#             return f"Directory created at: {path}"
#         else:
#             return f"Directory already exists: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to create directory: {str(e)}")
#
#
# create_directory_tool = StructuredTool.from_function(
#     func=create_directory,
#     name="CreateDirectory",
#     description="Creates a directory at the specified path.",
#     args_schema=DirectoryPathInput,
#     handle_tool_error=True
# )
#
#
# class FilePathInput(BaseModel):
#     path: str = Field(description="The path of the file on which an action will be applied.")
#
#
# class FileCreationInput(FilePathInput):
#     content: str = Field(default="", description="The content to write into the file.")
#
#
# def create_file_with_content(path: str, content: str = "") -> str:
#     """Creates a file at the specified path and writes the provided content to it."""
#     try:
#         with open(path, 'w') as file:
#             file.write(content)
#         return f"File created with content at: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to create file with content: {str(e)}")
#
#
# create_file_tool = StructuredTool.from_function(
#     func=create_file_with_content,
#     name="CreateFile",
#     description="Creates a file at the specified path and writes the provided content to it.",
#     args_schema=FileCreationInput,
#     handle_tool_error=True
# )
#
#
# def delete_file(path: str) -> str:
#     """Deletes the file at the specified path."""
#     try:
#         if exists(path):
#             os.remove(path)
#             return f"File deleted: {path}"
#         else:
#             return f"File does not exist: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to delete file: {str(e)}")
#
#
# delete_file_tool = StructuredTool.from_function(
#     func=delete_file,
#     name="DeleteFile",
#     description="Deletes the file at the specified path.",
#     args_schema=FilePathInput,  # Reusing the FilePathInput schema
#     handle_tool_error=True
# )
#
#
# def delete_directory(path: str) -> str:
#     """Deletes the directory at the specified path."""
#     try:
#         if exists(path):
#             rmtree(path)
#             return f"Directory deleted: {path}"
#         else:
#             return f"Directory does not exist: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to delete directory: {str(e)}")
#
#
# delete_directory_tool = StructuredTool.from_function(
#     func=delete_directory,
#     name="DeleteDirectory",
#     description="Deletes the directory at the specified path.",
#     args_schema=DirectoryPathInput,  # Reusing the DirectoryPathInput schema
#     handle_tool_error=True
# )
#
#
# def read_file_content(path: str) -> str:
#     """Reads and returns the content of the file at the specified path."""
#     try:
#         with open(path, 'r') as file:
#             content = file.read()
#         return content
#     except Exception as e:
#         raise ToolException(f"Failed to read file content: {str(e)}")
#
#
# read_file_content_tool = StructuredTool.from_function(
#     func=read_file_content,
#     name="ReadFileContent",
#     description="Reads and returns the content of the file at the specified path.",
#     args_schema=FilePathInput,
#     handle_tool_error=True
# )
#
#
# class VirtualEnvInput(BaseModel):
#     path: str = Field(description="The path where the virtual environment should be created.")
#
#
# def create_virtual_env(path: str) -> str:
#     """Creates a virtual environment at the specified path."""
#     try:
#         subprocess.run([f"python", "-m", "venv", path], check=True)
#         return f"Virtual environment created at: {path}"
#     except Exception as e:
#         raise ToolException(f"Failed to create virtual environment: {str(e)}")
#
#
# create_virtual_env_tool = StructuredTool.from_function(
#     func=create_virtual_env,
#     name="CreateVirtualEnv",
#     description="Creates a virtual environment at the specified path.",
#     args_schema=VirtualEnvInput,
#     handle_tool_error=True
# )
#
#
# class InstallRequirementsInput(BaseModel):
#     env_path: str = Field(description="The path to the virtual environment where the requirements should be installed.")
#     requirements_file: str = Field(description="The path to the requirements file.")
#
#
# def install_requirements_in_env(env_path: str, requirements_file: str) -> str:
#     """Installs requirements in the specified virtual environment from a requirements file."""
#     try:
#         # Determine the correct path for the Python executable based on the operating system
#         if platform.system() == "Windows":
#             python_executable = os.path.join(env_path, "Scripts", "python.exe")
#         else:
#             python_executable = os.path.join(env_path, "bin", "python")
#
#         # Execute the pip install command
#         subprocess.run([python_executable, "-m", "pip", "install", "-r", requirements_file], check=True)
#         return f"Requirements installed in virtual environment at: {env_path} from {requirements_file}"
#     except Exception as e:
#         raise ToolException(f"Failed to install requirements: {str(e)}")
#
#
# install_requirements_tool = StructuredTool.from_function(
#     func=install_requirements_in_env,
#     name="InstallRequirementsInEnv",
#     description="Installs requirements in the specified virtual environment from a requirements file.",
#     args_schema=InstallRequirementsInput,
#     handle_tool_error=True
# )
#
#
# class TestDirectoryInput(BaseModel):
#     test_dir: str = Field(description="The directory containing tests to run with pytest")
#     venv_python_path: str = Field(description="The path to the Python executable inside the venv")
#
#
# def run_pytest_in_directory(test_dir: str, venv_python_path: str = "") -> str:
#     """Runs pytest on all tests in the specified directory within a specified venv, returning detailed output."""
#     python_executable = venv_python_path if venv_python_path else "python"
#     pytest_command = [python_executable, "-m", "pytest", test_dir]
#
#     try:
#         result = subprocess.run(pytest_command, capture_output=True, text=True, check=True)
#         output = result.stdout + "\n" + result.stderr
#         return f"Tests executed successfully:\n{output}"
#     except subprocess.CalledProcessError as e:
#         # This captures errors from the subprocess itself and includes full output (stdout + stderr)
#         full_output = e.stdout + "\n" + e.stderr
#         raise ToolException(f"Failed to run tests with detailed output:\n{pytest_command}\n{full_output}\n")
#     except Exception as e:
#         # This captures any other exceptions, e.g., if the subprocess call fails to execute
#         raise ToolException(f"Failed to run tests: \n{pytest_command}\n{str(e)}")
#
# run_pytest_tool = StructuredTool.from_function(
#     func=run_pytest_in_directory,
#     name="RunPytest",
#     description="Runs pytest on all tests in the specified directory within a specified venv.",
#     args_schema=TestDirectoryInput,
#     handle_tool_error=True
# )
# TOOLS = [get_working_dir_tool, get_path_desktop_tool, change_working_dir_tool, create_directory_tool, create_file_tool,
#          delete_file_tool, delete_directory_tool, read_file_content_tool, install_requirements_tool,
#          create_virtual_env_tool, run_pytest_tool]
# NO_TOOLS = [change_working_dir_tool]