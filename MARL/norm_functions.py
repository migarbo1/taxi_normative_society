
UPPER_LEFT = 0
LEFT = 3

async def jump_queue_norm(agent):
    return agent.curr_state.view[UPPER_LEFT] == agent.curr_state.view[LEFT] == 1


async def jump_queue_penalty_callback(agent):
    agent.penalty = -90


async def confirm_move(agent):
    return agent.curr_action