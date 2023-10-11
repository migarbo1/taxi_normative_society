import random

async def jump_queue_penalty_callback(agent):
    agent.reputation -= 30


async def jump_queue_reward_callback(agent):
    agent.reputation += 10


async def max_working_hours_penalty_callback(agent):
    agent.reputation -= 10
    agent.recovery_ratio -= 0.1


async def max_working_hours_reward_callback(agent):
    agent.recovery_ratio += 0.03
    agent.reputation += 3


async def min_resting_time_penalty_callback(agent):
    agent.reputation -= 10


async def max_capacity_penalty_callback(agent):
    if random.random() > 0.65:
        print(f"Agent {agent.jid.localpart} encountered a police control while exceeding taxi capacity. Taxi license removed")
        await agent.stop()