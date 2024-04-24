from spade_norms.actions.normative_action import NormativeAction 
from spade_norms.engines.norm_engine import NormativeEngine
from spade_norms.norms.norm_enums import NormType
from spade_norms.norms.norm import Norm
from domain_and_roles import Domain, Role
from norm_functions import *
from taxi_agent import TaxiDriverAgent
from env_agent import EnvironmentAgent
import spade


async def main():
    n1 = Norm(
        'no_jump', 
        NormType.PROHIBITION, 
        jump_queue_norm, 
        inviolable=False, 
        domain=Domain.QUEUE, 
        roles=[Role.WORKING_DRIVER],
        penalty_cb=jump_queue_penalty_callback
    )

    a1 = NormativeAction(
        'confirm_move', 
        action_fn=confirm_move, 
        domain=Domain.QUEUE
        )
    
    normative_engine = NormativeEngine(norm=n1)

    env_agent = EnvironmentAgent(
        jid='env@your.xmpp.server', 
        password="password",
        episodes=10,
        steps_per_episode=20
    )
    taxi_agent = TaxiDriverAgent(
        agent_env_jid='env@your.xmpp.server',
        jid='taxidriver@your.xmpp.server', 
        password="password",
        num_features=11,
        num_actions=5,
        batch_size=64,
        weights='NMAS_target_nn',
        inference=True,
        normative_engine = normative_engine, 
        actions = [a1]
    )

    await env_agent.start()
    await taxi_agent.start()

spade.run(main())
