import json

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.agents import AgentFinish, AgentActionMessageLog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field

from llm import LLM

from tools.file_tools import create_directory_tool, create_file_tool, update_file_content_tool, read_file_content_tool


class File(BaseModel):
    """
    a representation of a file.
    """
    path: str = Field(description="the path of the file")
    description: str = Field(description="a description of the content of the file containing the signature of "
                                         "methods/classes/constants/... present in the file.")


class Result(BaseModel):
    """
    Return the result to the user request as a pydantic object
    """
    changed_files: list[File] = Field(description="a list of all files that where created or changed")
    entry_point: str = Field(description="The python file to run to start the software.")
    requirements: set[str] = Field(description="The requirements that need to be installed to run the project")


def replace_or_add_files(existing_files: list[dict], new_files: list[dict]) -> list[dict]:
    """
    Replaces existing files with files from the new_files list based on matching paths
    and adds new files if their paths do not exist in the existing files.

    :param existing_files: List of dictionaries representing existing files.
    :param new_files: List of dictionaries representing new files to replace the existing ones or to be added.
    :return: The updated list of dictionaries including replacements and additions.
    """
    # Convert existing_files list to a dictionary for faster lookup and uniqueness of path
    existing_files_dict = {file['path']: file for file in existing_files}

    for new_file in new_files:
        # Replace the existing file with the new one or add it if the path does not exist
        existing_files_dict[new_file['path']] = new_file

    # Convert the dictionary back to a list, now including both replacements and additions
    updated_files = list(existing_files_dict.values())

    return updated_files


def parse(output):
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the Project function was invoked, return to the user with the function inputs
    if name == "Result":
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )


def handle_step(state):
    """
    creates an agent that will handle a single step of the project plan.
    Args:
        state (dict): The state dict

    Returns:
        state (dict): New key added to state
    """
    print("---HANDLE STEP---")

    ## State
    state_dict = state["keys"]
    iterations = state_dict["iterations"]
    software_description = state_dict["software_description"]
    steps_done = state_dict["steps_done"]
    steps_todo = state_dict["steps_todo"]
    source = state_dict["source_folder"]
    test = state_dict["test_folder"]
    current_step = steps_todo[0]

    ## Prompt
    user_input = f"""
    I would like you to implement a given task. The final goal is to create:
    "{software_description}".

    In order to achieve this, this are the steps that have already been implemented:
    {steps_done}
    You only need to focus on the next step (this is your task):
    {current_step}

    Analyze what needs to be done, and add changes to the code where needed.
    Create files and folders if needed to keep the code organized. Aim to keep files small.
    All the code should be put in the source folder located at: {source} at started by running a single
    entry point python file.
    Also add tests (using pytest) for the new feature in the {test} folder.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are senior python developer. Use the provided tools to accomplish the task given by th user.
                """,
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", user_input),
        ]
    )

    # Tools
    tools = [create_directory_tool, create_file_tool, update_file_content_tool, read_file_content_tool, Result]
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
        tools=[create_directory_tool, create_file_tool, update_file_content_tool, read_file_content_tool],
        verbose=True
    )
    result = agent_executor.invoke({"input": ""}, return_only_outputs=True)

    iterations = iterations + 1
    state_dict["iterations"] = iterations
    updated_files = replace_or_add_files(state_dict["source_files"], result["changed_files"])
    state_dict["source_files"] = updated_files
    state_dict["entry_point"] = result["entry_point"]
    state_dict["requirements"] = state_dict["requirements"] | set(result["requirements"])
    state_dict["current_step"] = current_step

    return {
        "keys": state_dict
    }
