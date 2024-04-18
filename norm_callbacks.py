import random

#TODO

async def jump_queue_penalty_callback(agent):
    agent.decrease_reputation(0.20)


async def jump_queue_reward_callback(agent):
    agent.increase_reputation(0.025)


async def max_working_hours_penalty_callback(agent):
    agent.decrease_reputation(0.10)


async def max_working_hours_reward_callback(agent):
    agent.increase_reputation(0.033)


async def min_resting_time_penalty_callback(agent):
    agent.decrease_reputation(0.10)

