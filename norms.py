from spade_norms.norms.norm_enums import NormativeActionStatus

MAX_WORKING_TIME = 480e-3
RESTING_MINS = 30e-3

def jump_queue_norm(agent):
    if agent.taxi_queue.get_queue_pos(agent.jid.localpart) != 0:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED


def max_working_hours_norm(agent):
    if agent.worked_time >= MAX_WORKING_TIME:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED


def min_resting_time_norm(agent):
    if agent.current_rest_time < RESTING_MINS:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED


def capacity_norm(agent):
    if agent.taxi_capacity < agent.clients_at_sight:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED