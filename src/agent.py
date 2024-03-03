import os

from langgraph.graph import END, StateGraph
from typing import Dict, TypedDict

from states.create_project import create_project
from states.handle_step import handle_step
from states.generate_plan import generate_plan
from states.validate_plan import validate_plan, decide_to_recreate_plan

os.environ['LANGCHAIN_TRACING_V2'] = 'true'

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        keys: A dictionary where each key is a string.
    """

    keys: Dict[str, any]


def decide_done(state):
    """
    Determines whether to software is done

    Args:
       state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---IS EVERYTHING DONE?---")
    state_dict = state["keys"]
    steps_todo = state_dict["steps_todo"]
    steps_done = state_dict["steps_done"]
    plan_steps = state_dict["plan_steps"]

    if steps_todo is None and plan_steps == steps_done:
        print("---EVERYTHING IS DONE--")
        return "end"
    else:
        # We have relevant documents, so generate answer
        print("---THERE ARE STILL STEPS TO DO---")
        return "generate_plan"


async def coder_agent_model(input_str, history):
    workflow = StateGraph(GraphState)

    workflow.add_node("generate_plan", generate_plan)  # generation plan
    workflow.add_node("validate_plan", validate_plan)  # validate plan
    workflow.add_node("create_project", create_project)  # create the project folder and venv
    workflow.add_node("handle_step", handle_step)  # handle a step in the plan
    workflow.add_node("test_step", test_step)  # test the code

    workflow.add_edge("generate_plan", "validate_plan")
    workflow.add_conditional_edges(
        "validate_plan",
        decide_to_recreate_plan,
        {
            "generate_plan": "generate_plan",
            "create_project": "create_project",
        },
    )
    workflow.add_edge("create_project", "handle_step")
    workflow.add_edge("handle_step", "test_step")
    workflow.add_edge("test_step", END)

    workflow.set_entry_point("generate_plan")

    # Compile
    config = {"recursion_limit": 20}
    app = workflow.compile()

    # Construct the correct input structure
    inputs = {
        "keys": {
            "software_description": input_str,
            "iterations": 0
        }
    }

    output_lines = []
    async for chunk in app.astream(inputs, config=config):
        output_lines.append('\n')
        if 'generate_plan' in chunk:
            output_lines.extend(["___Generated Plan:___"])
            output_lines.extend(["Project name: " + chunk['generate_plan']['keys']['project_name']])
            output_lines.extend(chunk['generate_plan']['keys']['plan_steps'])

        if 'validate_plan' in chunk:
            output_lines.extend(["___Validate Plan:___"])
            value = "OK" if chunk['validate_plan']['keys']['plan_ok'] else "not OK"
            output_lines.extend([f"Plan is {value}"])
            if chunk['validate_plan']['keys']['plan_feedback']:
                output_lines.extend(["Feedback:"])
                output_lines.extend([chunk['validate_plan']['keys']['plan_feedback']])

        if 'create_project' in chunk:
            output_lines.extend(["___Creating project:___"])
            output_lines.extend(["Project folder: " + chunk['create_project']['keys']['project_folder']])
            output_lines.extend(["Test folder: " + chunk['create_project']['keys']['test_folder']])
            output_lines.extend(["Source folder: " + chunk['create_project']['keys']['source_folder']])
            output_lines.extend(["Python path in venv: " + chunk['create_project']['keys']['python_path']])

        if 'handle_step' in chunk:
            output_lines.extend(["___Handel step:___"])
            output_lines.extend([chunk['handle_step']['keys']['current_step']])
            output_lines.extend(["start program with script: " + chunk['handle_step']['keys']['entry_point']])
            output_lines.extend(["current files:"])
            for file in chunk['handle_step']['keys']['source_files']:
                output_lines.extend([file['path'] + ": " + file['description']])
            output_lines.extend(["current requirements: " + str(chunk['handle_step']['keys']['requirements'])])

        yield '\n'.join(output_lines)
