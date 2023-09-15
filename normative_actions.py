from fsm_taxi_behaviour import DriverState
from domain_and_roles import Role

def jump_queue(agent):
    print(f"[{agent.jid.localpart}] JUMPING to first position of the queue")
    agent.taxi_queue.remove_from_queue(agent.jid.localpart)
    agent.taxi_queue.add_to_start_of_queue(agent.jid.localpart)


async def resume_work(agent):
    print(f"[{agent.jid.localpart}] RESUMING to work")
    async with agent.q_semaphore:
        agent.role = Role.WORKING_DRIVER
        agent.taxi_queue.add_to_end_of_queue(agent.jid.localpart)
        current_state_name = agent.behaviours[0].current_state
        agent.behaviours[0]._states[current_state_name].set_next_state(DriverState.WAITING)