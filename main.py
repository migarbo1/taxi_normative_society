import asyncio
from normative_actions import *
from norms import *
from spade_norms.actions.normative_action import NormativeAction 
from spade_norms.norms.norm import Norm
from spade_norms.norms.norm_enums import NormType
from spade_norms.engines.norm_engine import NormativeEngine
from taxi_driver_agent import TaxiDriverAgent
import spade
from queue_utils import TaxiQueue
from domain_and_roles import *
import random


random.seed(33)


def create_norms():
    norms = [
        Norm('no_jump', NormType.PROHIBITION, jump_queue_norm, inviolable=False, domain=Domain.QUEUE, roles=[Role.WORKING_DRIVER]),
        Norm('no_overwork', NormType.PROHIBITION, max_working_hours_norm, inviolable=False, domain=Domain.SCHEDULE, roles=[Role.WORKING_DRIVER]),
        Norm('no_under-rest', NormType.PROHIBITION, min_resting_time_norm, inviolable=False, domain=Domain.SCHEDULE, roles=[Role.RESTING_DRIVER]),
        Norm('no_exceed_capacity', NormType.PROHIBITION, capacity_norm, inviolable=False, domain=Domain.QUEUE, roles=[Role.WORKING_DRIVER])
    ]
    return norms


def create_actions():
    actions = [
        NormativeAction('jump_queue', action_fn=jump_queue, domain=Domain.QUEUE),
        NormativeAction('resume_work', action_fn=resume_work, domain=Domain.SCHEDULE),
        NormativeAction('pick_clients', action_fn=pickup_clients, domain=Domain.QUEUE)
    ]
    return actions


async def main(num_agents = 4):
    taxi_queue = TaxiQueue()
    q_semaphore = asyncio.Semaphore(1)

    normative_engine = NormativeEngine(norm_list=create_norms())

    for i in range(num_agents):
        taxi_agent = TaxiDriverAgent(
            jid='taxi_driver{}@your.xmpp.server'.format(i), 
            password="password",
            queue=taxi_queue,
            semaphore = q_semaphore,
            normative_engine = normative_engine, 
            actions = create_actions(),
            role=Role.WORKING_DRIVER
        )
    
        await taxi_agent.start()


if __name__ == '__main__':
    spade.run(main())