import json
from typing import Optional

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.agents import AgentFinish, AgentActionMessageLog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field

from llm import LLM

from tools.venv_tools import create_requirements_file_tool, install_requirements_tool

from tools.python_tools import run_pytest_tool


class Result(BaseModel):
    """
    Return the result to the user request as a pydantic object
    """
    feedback: Optional[str] = Field(description="Feedback if the test failed to run. Also contains the output of the "
                                                "test run")
    result: bool = Field(description="True if the tests succeeded, False otherwise")


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


def test_step(state):
    """
    creates an agent that will handle a single step of the project plan.
    Args:
        state (dict): The state dict

    Returns:
        state (dict): New key added to state
    """
    print("---TEST STEP---")

    ## State
    state_dict = state["keys"]
    iterations = state_dict["iterations"]
    project_folder = state_dict["project_folder"]
    requirements = state_dict["requirements"]
    test = state_dict["test_folder"]
    ## Prompt

    user_input = f"""
    This is the project folder path:{project_folder}
    This is a list of requirements: {str(list(requirements))}
    This is the path to the test folder : {test}
    1. create a requirements file for the requirements
    2. install the requirements in the venv
    3. run the test using pytest
    when done, return the output as a pydantic object
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
    tools = [create_requirements_file_tool, install_requirements_tool, run_pytest_tool, Result]
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
        tools=[create_requirements_file_tool, install_requirements_tool, run_pytest_tool],
        verbose=True
    )
    result = agent_executor.invoke({"input": ""}, return_only_outputs=True)

    iterations = iterations + 1
    state_dict["iterations"] = iterations
    state_dict["test_result"] = result["result"]
    state_dict["test_feedback"] = result["feedback"] if "feedback" in result else ""

    return {
        "keys": state_dict
    }


def decide_rework_code(state):
    """
    Determines if we continue or if the code needs to be reworked.

    Args:
       state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---SHOULD REWORK CODE?---")
    state_dict = state["keys"]
    success = state_dict["test_result"]
    if success is True:
        print("---TEST PASSED: LET'S CONTINUE")
        return "finish"
    else:
        # We have relevant documents, so generate answer
        print("---TEST FAILED: NEED TO REWORK CODE")
        return "rework_code"
