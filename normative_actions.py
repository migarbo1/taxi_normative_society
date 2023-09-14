import queue_utils as qu

def jump_queue(agent):
    print(f"{agent.jid.localpart} is JUMPING at first position in the queue with ROLE {agent.role}")
    agent.taxi_queue.remove_from_queue(agent.jid.localpart)
    agent.taxi_queue.add_to_start_of_queue(agent.jid.localpart)
