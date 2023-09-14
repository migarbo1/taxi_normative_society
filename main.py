import asyncio
from normative_actions import jump_queue
from norms import jump_queue_norm
from spade_norms.actions.normative_action import NormativeAction 
from spade_norms.norms.norm import Norm
from spade_norms.norms.norm_enums import NormType
from spade_norms.engines.norm_engine import NormativeEngine
from taxi_driver_agent import TaxiDriverAgent
import spade
from queue_utils import TaxiQueue


async def main(num_agents = 4):
    taxi_queue = TaxiQueue()
    q_semaphore = asyncio.Semaphore(1)

    jump_queue_action = NormativeAction('jump_queue', jump_queue)

    jump_norm = Norm(
        'no-jump',
        NormType.PROHIBITION,
        jump_queue_norm,
        inviolable=False
    )

    normative_engine = NormativeEngine(norm_list=[jump_norm])

    for i in range(num_agents):
        taxi_agent = TaxiDriverAgent(
            jid='taxi_driver{}@gtirouter.dsic.upv.es'.format(i), 
            password="password",
            queue=taxi_queue,
            semaphore = q_semaphore,
            normative_engine = normative_engine, 
            actions = [jump_queue_action])
    
        await taxi_agent.start()


if __name__ == '__main__':
    spade.run(main())