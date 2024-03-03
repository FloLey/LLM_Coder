import json

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.agents import AgentFinish, AgentActionMessageLog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field

from llm import LLM

from tools.file_tools import create_directory_tool, create_file_tool, update_file_content_tool, read_file_content_tool

from helpers import read_files_in_directory_as_string


class Result(BaseModel):
    """
    Return the result to the user request as a pydantic object
    """
    description: str = Field(description="A detailed explanation of what was implemented.")
    requirements: list[str] = Field(description="A list of requirements that need to be installed to run the code")

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

    ## State
    state_dict = state["keys"]

    iterations = state_dict["iterations"]
    software_description = state_dict["software_description"]
    steps_done = state_dict["steps_done"]
    steps_todo = state_dict["steps_todo"]
    source = state_dict["source_folder"]
    test = state_dict["test_folder"]
    current_step = steps_todo[0]

    src_files = read_files_in_directory_as_string(source)
    test_files = read_files_in_directory_as_string(test)

    print("---HANDLE STEP---")
    user_input = f"""
    I would like you to implement a given task. The final goal is to create:
    "{software_description}".

    In order to achieve this, this are the steps that have already been implemented:
    {steps_done}
    You only need to focus on the next step (this is your task):
    {current_step}
    
    here are the current source files:
    {src_files}
    
    here are the test files:
    {test_files}

    Analyze what needs to be done, and add changes to the code where needed.
    Always make minimal changes and make sure the code is documented with docstrings.
    Create files and folders if needed to keep the code organized. Aim to keep files small.
    All the code should be put in the source folder located at: {source} and started by running a single
    entry point python file.
    Also add tests (using pytest) for the new feature in the {test} folder. 
    When importing packages, keep in mind that the src and test folder are at the same level.
    keep track of the requirements that need to be installed to run the code.
    Return the result as a pydantic object
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
    tools = [create_directory_tool, create_file_tool, update_file_content_tool, Result]
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
        tools=[create_directory_tool, create_file_tool, update_file_content_tool],
        verbose=True
    )
    result = agent_executor.invoke({"input": ""}, return_only_outputs=True)
    iterations = iterations + 1
    state_dict["iterations"] = iterations
    state_dict["requirements"] = set(result["requirements"])
    state_dict["current_step_description"] = result["description"]
    state_dict["current_step"] = current_step

    return {
        "keys": state_dict
    }
