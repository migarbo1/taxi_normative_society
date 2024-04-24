from env import Action, TaxiGridEnv
from spade.agent import Agent
from state import State
import spade
import json


class EnvironmentAgent(Agent):

    def __init__(self, episodes, steps_per_episode,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = TaxiGridEnv()
        demo_state = State(0,0)
        self.num_features = len(demo_state.to_array())
        self.num_actions = len(Action)
        self.agent_states = {}
        self.episodes = episodes
        self.curr_episodes = 0
        self.steps_per_episode = steps_per_episode
        self.curr_steps = 0

    
    async def setup(self) -> None:
        template = spade.template.Template(metadata={"performative": "Register"})
        self.add_behaviour(self.RegisterBehaviour(), template)

        template = spade.template.Template(metadata={"performative": "StepResponse"})
        self.add_behaviour(self.StepBehaviour(), template)

        self.add_behaviour(self.EndBehaviour())
    

    class RegisterBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                agent = str(msg.sender)
                if self.agent.agent_states.get(agent, []) == []:
                    state = self.agent.env.register_driver() 
                    self.agent.agent_states[agent] = State.to_json(state)


    class StepBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):

            for agent in self.agent.agent_states.keys():
                state = self.agent.agent_states[agent]
                body = json.dumps({'state': state})
                msg = spade.message.Message(to=agent, body=body, metadata={"performative": "StepRequest"})
                await self.send(msg)
                rsp = await self.receive(timeout=10)
                body = json.loads(rsp.body)
                action = int(body['action'])
                reward, o_next_state = self.agent.env.step(State.from_json(state), action)
                body = json.dumps({'reward':reward, 'state': State.to_json(o_next_state)})
                self.agent.agent_states[agent] = State.to_json(o_next_state)
                msg = spade.message.Message(to=agent, body=body, metadata={"performative": "RewardResponse"})
                await self.send(msg)
                self.agent.curr_steps += 1
                if self.agent.curr_steps % self.agent.steps_per_episode == 0:
                    self.agent.curr_episodes += 1


    class EndBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            if self.agent.curr_episodes == self.agent.episodes:
                for agent in self.agent.agent_states.keys():
                    msg = spade.message.Message(to=agent, body='', metadata={"performative": "Stop"})
                    await self.send(msg)
                await self.agent.stop()
