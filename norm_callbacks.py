import random

#TODO

async def jump_queue_penalty_callback(agent):
    agent.decrease_reputation(0.3)


async def jump_queue_reward_callback(agent):
    agent.increase_reputation(0.10)


async def max_working_hours_penalty_callback(agent):
    agent.decrease_reputation(0.10)
    agent.recovery_ratio -= 0.1


async def max_working_hours_reward_callback(agent):
    agent.recovery_ratio += 0.03
    agent.increase_reputation(0.3)


async def min_resting_time_penalty_callback(agent):
    agent.decrease_reputation(0.10)


async def max_capacity_penalty_callback(agent):
    if random.random() > 0.75:
        print(f"Agent {agent.jid.localpart} encountered a police control while exceeding taxi capacity. Taxi license removed")
        await agent.stop()