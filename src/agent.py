import os

from langgraph.graph import END, StateGraph
from typing import Dict, TypedDict

from states.prepare_next import prepare_next_step, decide_finished
from states.rework_code import rework_code
from states.test_step import test_step, decide_rework_code
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
    workflow.add_node("rework_code", rework_code)  # test the code
    workflow.add_node("prepare_next_step", prepare_next_step)  # prepare for next step


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
    workflow.add_conditional_edges(
        "test_step",
        decide_rework_code,
        {
            "rework_code": "rework_code",
            "prepare_next_step": "prepare_next_step",
        },
    )

    workflow.add_edge("rework_code", "test_step")

    workflow.add_conditional_edges(
        "prepare_next_step",
        decide_finished,
        {
            "handle_step": "handle_step",
            "FINISH": END,
        },
    )

    workflow.set_entry_point("generate_plan")

    # Compile
    config = {"recursion_limit": 100}
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
            output_lines.extend(["Step description: "])
            output_lines.extend([str(chunk['handle_step']['keys']['current_step_description'])])
            output_lines.extend(["current requirements: " + str(chunk['handle_step']['keys']['requirements'])])

        if 'test_step' in chunk:
            output_lines.extend(["___Test step:___"])
            output_lines.extend([chunk['test_step']['keys']['current_step']])
            value = "OK" if chunk['test_step']['keys']['test_result'] else "not OK"
            output_lines.extend([f"Test result: {value}"])
            if chunk['test_step']['keys']['test_feedback']:
                output_lines.extend(["Feedback:"])
                output_lines.extend([chunk['test_step']['keys']['test_feedback']])

        if 'rework_code' in chunk:
            output_lines.extend(["___Rework code step:___"])
            output_lines.extend([chunk['rework_code']['keys']['current_step']])
            output_lines.extend(["Step description: "])
            output_lines.extend([str(chunk['rework_code']['keys']['current_rework_description'])])
            output_lines.extend(["current requirements: " + str(chunk['rework_code']['keys']['requirements'])])

        if 'prepare_next_step' in chunk:
            if len(chunk['prepare_next_step']['keys']['steps_todo']):
                output_lines.extend(["___Preparing next step:___"])
                output_lines.extend(["To do: "])
                output_lines.extend([str(chunk['prepare_next_step']['keys']['steps_todo'])])
                output_lines.extend(["Done: "])
                output_lines.extend([str(chunk['prepare_next_step']['keys']['steps_done'])])
            else:
                output_lines.extend(["___Done___"])
                output_lines.extend(["The program should now be ready :)"])
        yield '\n'.join(output_lines)
