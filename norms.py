from spade_norms.norms.norm_enums import NormativeActionStatus

MAX_WORKING_HOURS = 4
RESTING_MINS = 30

def jump_queue_norm(agent):
    return NormativeActionStatus.FORBIDDEN


def max_working_hours_norm(agent):
    if agent.worked_hours >= MAX_WORKING_HOURS:
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