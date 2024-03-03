from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers.openai_tools import PydanticToolsParser

from llm import LLM


class Plan(BaseModel):
    """A plan to develop a software step by step with a name for the software"""
    description: str = Field(description="Description of the problem and approach")
    steps: list[str] = Field(description="A list of steps that need to be taken to solve the problem")
    project_name: str = Field(description="A suitable name for the project based on the description")


def generate_plan(state):
    """
    Generate a plan to develop a software step by step

    Args:
        state (dict): The state dict

    Returns:
        state (dict): New key added to state
    """

    ## State
    state_dict = state["keys"]
    software_description = state_dict["software_description"]
    iterations = state_dict["iterations"]

    ## LLM
    llm_with_tool = LLM.bind_tools([Plan])

    # Parser
    parser_tool = PydanticToolsParser(tools=[Plan])

    ## Prompt
    template = """"As a python software architect, you will receive specifications or requirements for a software project. 
    Your primary task is to decompose the overall problem into manageable, executable steps or sub-problems. 
    Each step should be designed in such a way that, upon completion, the software is in a functional state, 
    even if it does not yet include all the planned features or capabilities. Each step should add or change code.

    Please follow these guidelines when breaking down the software project:
    1. Identify Key Components: Determine the core components or modules that make up the software system. 
        These components should reflect major functional areas of the software.
    2. Sequential Steps: Organize the development process into sequential steps. 
        Each step should focus on implementing a specific component or enhancing the software's functionality progressively.
    3. Ensure Functionality at Each Stage: Design each step so that the software remains operational and can perform a 
        subset of its intended functions after the step is completed.

    Here is the description of the software project you will be working on: 
    {software_description}

    Please proceed by breaking down the project into a list of detailed steps, 
    keeping in mind the goal of maintaining software functionality throughout the development process.
    Don't mention testing as it is not your responsibility. Also find a suitable name for the project.
    """

    ## Generation
    if "plan_feedback" in state_dict:
        print("---RE-GENERATE PLAN w/ FEEDBACK---")

        feedback = state_dict["plan_feedback"]
        plan_steps = state_dict["plan_steps"]
        # Update prompt
        template = """
As a python software architect tasked with refining a software development plan, 
you are asked to enhance the project's trajectory based on received feedback.

Software Description: {software_description}

Proposed Steps: 
{plan_steps}

Received Feedback:

{feedback}

Revision Guidelines:

Reflect on Feedback: Carefully consider the feedback provided, identifying specific areas where the 
initial plan can be improved or adjusted to better meet the project's needs.

Please proceed by breaking down the project into detailed steps, 
Don't mention testing and documentation as it is not your responsibility. Also find a suitable name for the project.       
"""
        # Prompt
        prompt = PromptTemplate(
            template=template,
            input_variables=["software_description", "feedback", "plan_steps"],
        )

        # Chain
        chain = (
                {
                    "software_description": itemgetter("software_description"),
                    "feedback": itemgetter("feedback"),
                    "plan_steps": itemgetter("plan_steps"),
                }
                | prompt
                | llm_with_tool
                | parser_tool
        )
        plan = chain.invoke({
            "software_description": software_description,
            "feedback": feedback,
            "plan_steps": plan_steps,
        })

    else:
        print("---GENERATE PLAN---")

        # Prompt
        prompt = PromptTemplate(
            template=template,
            input_variables=["software_description"],
        )

        # Chain
        chain = (
                {
                    "software_description": itemgetter("software_description"),
                }
                | prompt
                | llm_with_tool
                | parser_tool
        )

        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            try:
                plan = chain.invoke({"software_description": software_description})
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
    state_dict["plan_description"] = plan[0].description
    state_dict["plan_steps"] = plan[0].steps
    state_dict["steps_todo"] = plan[0].steps
    state_dict["steps_done"] = []
    state_dict["project_name"] = plan[0].project_name

    return {
        "keys": state_dict
    }
