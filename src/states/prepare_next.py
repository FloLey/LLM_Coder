def move_first_todo_to_done(state_dict):
    """
    Moves the first item from the 'todos' list to the 'done' list within a dictionary.

    :param state_dict: Dictionary with 'todos' and 'done' lists.
    """
    # Check if there's at least one task in the 'todos' list
    if state_dict['steps_todo']:
        # Remove the first task from the 'todos' list and store it
        task_to_move = state_dict['steps_todo'].pop(0)
        # Append the removed task to the 'done' list
        state_dict['steps_done'].append(task_to_move)
    else:
        raise Exception("No tasks in 'todos' list to move.")


def prepare_next_step(state):
    """
    prepare the agent for the next step

    Args:
        state (dict): The state dict

    Returns:
        state (dict): New key added to state
    """
    ## State
    state_dict = state["keys"]
    move_first_todo_to_done(state_dict)

    return {
        "keys": state_dict
    }


def decide_finished(state):
    """
    Determines whether to test code execution, or re-try answer generation.

    Args:
       state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ARE WE DONE?---")
    state_dict = state["keys"]
    todos = state_dict['steps_todo']
    if len(todos) == 0:
        print("---WE ARE DONE :D--")
        return "FINISH"
    else:
        # We have relevant documents, so generate answer
        print("---THERE ARE STILL SOME STEPS TO DO---")
        return "handle_step"
