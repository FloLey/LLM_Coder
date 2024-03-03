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
    description: str = Field(description="A detailed explanation of what was changed")
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


def rework_code(state):
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
    source = state_dict["source_folder"]
    test = state_dict["test_folder"]
    step_description = ["current_step_description"]

    src_files = read_files_in_directory_as_string(source)
    test_files = read_files_in_directory_as_string(test)

    feedback = state_dict["test_feedback"]

    user_input = f"""
I would like you fix/rework existing code.

Here is a description of the changes that where made. Before the changes the test where passing:
{step_description}

here are the current source files:
{src_files}

here are the test files:
{test_files}

here is the output that was created when running test:
{feedback}

Analyze what needs to be done, and change to the code where needed.
Make sure the code is documented with docstrings.
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
    tools = [update_file_content_tool, Result]
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
        tools=[update_file_content_tool],
        verbose=True
    )
    result = agent_executor.invoke({"input": ""}, return_only_outputs=True)
    iterations = iterations + 1
    state_dict["iterations"] = iterations
    state_dict["requirements"] = set(result["requirements"])
    state_dict["current_rework_description"] = result["description"]

    return {
        "keys": state_dict
    }
