import json

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.agents import AgentFinish, AgentActionMessageLog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field

from llm import LLM

from tools.file_tools import create_directory_tool
from tools.venv_tools import create_virtual_env_tool
from tools.file_tools import create_file_tool

WORKDIR = "/home/florent/Desktop/test_code_generator"



class Project(BaseModel):
    """
    Return the result to the user request as a pydantic object
    """
    project_folder: str = Field(description="The path to the project folder")
    source_folder: str = Field(description="The path to the source folder")
    test_folder: str = Field(description="The path to the test folder")
    python_path: str = Field(description="The path to python executable")


def parse(output):
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the Project function was invoked, return to the user with the function inputs
    if name == "Project":
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )


def create_project(state):
    """
    create a folder for the project and a virtual environment in the folder for the project.
    Args:
        state (dict): The state dict

    Returns:
        state (dict): New key added to state
    """

    print("---CREATE PROJECT AND VENV---")

    ## State
    state_dict = state["keys"]
    iterations = state_dict["iterations"]
    project_name = state_dict["project_name"]

    ## Prompt
    user_input = f"""
    This is the name of the project: {project_name}. The folder name should be curated.
    This is the location where you should create a folder for the project: {WORKDIR}

    1. Create a single folder for the project using the project name
    2. Create an empty "conftest.py" file at the root of the project
    3. Create a single new virtual environment in a venv folder in the project folder
    4. Create a single "src" folder in the project folder
    5. Create a single "tests" folder in the project folder
    6. Return the result as a pydantic object
    
        """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are senior python developer. Use the provided tools to accomplish the task given by the user.
                """,
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", user_input),
        ]
    )

    # Tools
    tools = [create_virtual_env_tool, create_directory_tool, create_file_tool, Project]
    llm_with_tools = LLM.bind_functions(tools)
    agent = (
            {
                "input": lambda x: x["input"],
                # Format agent scratchpad from intermediate steps
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | parse
    )
    agent_executor = AgentExecutor(
        agent=agent,
        tools=[create_virtual_env_tool, create_directory_tool, create_file_tool],
        verbose=True
    )

    result = agent_executor.invoke({"input": ""}, return_only_outputs=True)

    iterations = iterations + 1
    state_dict["iterations"] = iterations
    state_dict["project_folder"] = result["project_folder"]
    state_dict["source_folder"] = result["source_folder"]
    state_dict["test_folder"] = result["test_folder"]
    state_dict["python_path"] = result["python_path"]
    state_dict["requirements"] = set()

    return {
        "keys": state_dict
    }
