from operator import itemgetter
from typing import Optional

from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers.openai_tools import PydanticToolsParser

from llm import LLM


class ValidatePlan(BaseModel):
    """A validation of a plan to develop a software step by step"""
    feedback: str = Field(description="Feedback on the validated plan, only required if the plan seems wrong")
    is_ok: bool = Field(description="True if the plan doesn't need feedback, False if it needs to be reworked")


def validate_plan(state):
    """
    validate a plan to develop a software step by step

    Args:
        state (dict): The state dict

    Returns:
        state (dict): New key added to state
    """

    ## State
    state_dict = state["keys"]
    software_description = state_dict["software_description"]
    iterations = state_dict["iterations"]
    plan_steps = state_dict["plan_steps"]

    ## LLM
    llm_with_tool = LLM.bind_tools([ValidatePlan])

    # Parser
    parser_tool = PydanticToolsParser(tools=[ValidatePlan])

    ## Prompt
    template = """As python software development processes specialist, your role is to review and validate a software 
    development plan. You will be provided with a description of the software project, along with a series of steps 
    proposed for its development. Your task involves evaluating the plan to ensure that it meets the project's 
    requirements, is structured to facilitate a smooth, iterative development process. Do not mention testing and 
    documentation.

Here is the description of the software project and the proposed development plan you will be validating:

software desciption: 
{software_description}

Development steps:
{plan_steps}

Based on the above information, proceed with the validation of the development plan. 
Don't be to strict, only reject a plan if it is something is wrong.
    """

    print("---VALIDATE PLAN---")

    # Prompt
    prompt = PromptTemplate(
        template=template,
        input_variables=["software_description", "plan_steps"],
    )

    # Chain
    chain = (
            {
                "software_description": itemgetter("software_description"),
                "plan_steps": itemgetter("plan_steps"),
            }
            | prompt
            | llm_with_tool
            | parser_tool
    )

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            plan_validation = chain.invoke({
                "software_description": software_description,
                "plan_steps": '\n'.join(plan_steps)
            })
            break
        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts} failed with error: {e}")
            if attempts >= max_attempts:
                raise e
            else:
                print(f"Retrying... Attempt {attempts + 1}/{max_attempts}")

    iterations = iterations + 1
    state_dict["iterations"] = iterations
    state_dict["plan_feedback"] = plan_validation[0].feedback
    state_dict["plan_ok"] = plan_validation[0].is_ok
    return {
        "keys": state_dict
    }


def decide_to_recreate_plan(state):
    """
    Determines whether to test code execution, or re-try answer generation.

    Args:
       state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---SHOULD RECREATE PLAN?---")
    state_dict = state["keys"]
    is_ok = state_dict["plan_ok"]
    if is_ok is True:
        print("---DECISION: PLAN IS OK--")
        return "create_project"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: PLAN NEEDS REWORK---")
        return "generate_plan"
