from spade_norms.norms.norm_enums import NormativeActionStatus
from problem_constants import constants


def jump_queue_norm(agent):
    if agent.taxi_queue.get_queue_pos(agent.jid.localpart) != 0:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED


def max_working_hours_norm(agent):
    if agent.worked_time >= constants['max_working_time']:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED


def min_resting_time_norm(agent):
    if agent.current_rest_time < constants['min_resting_time']:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED


def capacity_norm(agent):
    if agent.taxi_capacity < agent.clients_at_sight:
        return NormativeActionStatus.FORBIDDEN
    return NormativeActionStatus.ALLOWED