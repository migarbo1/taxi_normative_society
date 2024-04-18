import asyncio
from normative_actions import *
from norms import *
from spade_norms.actions.normative_action import NormativeAction 
from spade_norms.norms.norm import Norm
from spade_norms.norms.norm_enums import NormType
from spade_norms.engines.norm_engine import NormativeEngine
from reasoning_engines import *
from taxi_driver_agent import TaxiDriverAgent
import spade
from queue_utils import TaxiQueue
from domain_and_roles import *
import random
import asyncio
from norm_callbacks import *
from problem_constants import constants
import sys


random.seed(33)


def create_norms():
    norms = [
        Norm('no_jump', NormType.PROHIBITION, jump_queue_norm, inviolable=False, domain=Domain.QUEUE, roles=[Role.WORKING_DRIVER], reward_cb=jump_queue_reward_callback, penalty_cb=jump_queue_penalty_callback),
        Norm('no_overwork', NormType.PROHIBITION, max_working_hours_norm, inviolable=False, domain=Domain.SCHEDULE, roles=[Role.WORKING_DRIVER], reward_cb=max_working_hours_reward_callback, penalty_cb=max_working_hours_penalty_callback),
        Norm('no_under-rest', NormType.PROHIBITION, min_resting_time_norm, inviolable=False, domain=Domain.SCHEDULE, roles=[Role.RESTING_DRIVER], penalty_cb=min_resting_time_penalty_callback),
        Norm('no_exceed_capacity', NormType.PROHIBITION, capacity_norm, inviolable=True, domain=Domain.QUEUE, roles=[Role.WORKING_DRIVER])
    ]
    return norms


def create_actions():
    actions = [
        NormativeAction('jump_queue', action_fn=jump_queue, domain=Domain.QUEUE),
        NormativeAction('resume_work', action_fn=resume_work, domain=Domain.SCHEDULE),
        NormativeAction('pick_clients', action_fn=pickup_clients, domain=Domain.QUEUE)
    ]
    return actions


async def main(ag_type):
    taxi_queue = TaxiQueue()
    q_semaphore = asyncio.Semaphore(1)

    normative_engine = NormativeEngine(norm_list=create_norms())
    agents = []

    for i in range(constants['num_of_agents']):
        if ag_type == 0:
            reasoning_engine = None
        if ag_type == 1:
            reasoning_engine = ComplexMoneyDrivenReasoningEngine() 
        if ag_type == 2:
            reasoning_engine = ComplexMoneyDrivenReasoningEngine() if i % 2 == 0 else None

        taxi_agent = TaxiDriverAgent(
            jid='taxi_driver{}@your.xmpp.server'.format(i), 
            password="password",
            queue=taxi_queue,
            semaphore = q_semaphore,
            normative_engine = normative_engine, 
            reasoning_engine = reasoning_engine,
            actions = create_actions(),
            role=Role.WORKING_DRIVER,
            num_agents = constants['num_of_agents']
        )

        await taxi_agent.start()
        taxi_agent.web.start(hostname="127.0.0.1", port=int(f'808{i}'))
        taxi_agent.join_queue_first_time()

        agents.append(taxi_agent)
    
    await asyncio.sleep(constants['simulation_time']/2)

    for i in range(constants['num_of_agents']):
        print(f"{'NormFollower' if agents[i].normative.reasoning_engine != None else 'NormBreaker'}Agent,{agents[i].earned_money:.2f},{agents[i].reputation:.2f},{agents[i].num_jobs_lost:.0f},{agents[i].sucessful_pickup_count:.0f},{agents[i].normative.total_norms_broken:.2f}")
    print()
    exit()


if __name__ == '__main__':
    if len(sys.argv)>1:
        ag_type = int(sys.argv[1])
    spade.run(main(ag_type))