from spade_norms.spade_norms import NormativeMixin
from exp_replay_buffer import ReplayBuffer
from state import State
import torch.nn.functional as F
from spade.agent import Agent
from network import DQN
from env import Action
import torch.nn as nn
import numpy as np
import random
import torch
import spade
import json
import os

class TaxiDriverAgent(NormativeMixin, Agent):

    def __init__(self, agent_env_jid, num_features, num_actions, batch_size, weights='target_nn', inference=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env_jid = agent_env_jid
        self.inference = inference
        self.epsilon = 0.5
        self.batch_size = batch_size
        self.weights = weights
        self.num_actions = num_actions
        self.penalty = 0

        self.setup_networks(num_features, num_actions, weights)


    def setup_networks(self, feats, acts, weights):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.replay_buffer = ReplayBuffer(100000, device=self.device)

        self.main_nn = DQN(feats, acts).to(self.device)
        self.trgt_nn = DQN(feats, acts).to(self.device)

        self.opt = torch.optim.Adam(self.main_nn.parameters(), lr=1e-3)
        self.loss_fn = nn.MSELoss()

        if os.path.exists(f'{os.getcwd()}/weights/{weights}.pth'):
            if self.device == torch.device("cpu"):
                self.main_nn.load_state_dict(torch.load(f'{os.getcwd()}/weights/{weights}.pth', map_location=torch.device('cpu')))
                self.trgt_nn.load_state_dict(torch.load(f'{os.getcwd()}/weights/{weights}.pth', map_location=torch.device('cpu')))
            else:
                self.main_nn.load_state_dict(torch.load(f'{os.getcwd()}/weights/{weights}.pth'))
                self.trgt_nn.load_state_dict(torch.load(f'{os.getcwd()}/weights/{weights}.pth'))


    def train_step(self, states, actions, rewards, next_states, discount = 0.99):
        max_next_qs = self.trgt_nn(next_states).max(-1).values
        target = rewards + discount * max_next_qs
        qs = self.main_nn(states)
        action_masks = F.one_hot(actions, self.num_actions)
        masked_qs = (action_masks * qs).sum(dim=-1)
        loss = self.loss_fn(masked_qs, target.detach())
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()
        return loss


    def select_epsilon_greedy_action(self, state, epsilon, inference = False):
        st = torch.from_numpy(np.expand_dims(state, axis=0)).to(self.device)
        if inference:
            qs = self.trgt_nn(st).cpu().data.numpy()
            return np.argmax(qs)

        if np.random.uniform() < epsilon:
            return int(random.choice(list(Action)).value)
        else:
            qs = self.main_nn(st).cpu().data.numpy()
            return np.argmax(qs)


    async def setup(self) -> None:
        self.add_behaviour(self.RegisterBehaviour())

        template = spade.template.Template(metadata={"performative": "StepRequest"})
        self.add_behaviour(self.StepBehaviour(), template)

        template = spade.template.Template(metadata={"performative": "RewardResponse"})
        self.add_behaviour(self.RewardBehaviour(), template)

        template = spade.template.Template(metadata={"performative": "Stop"})
        self.add_behaviour(self.StopBehaviour(), template)
    

    class RegisterBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self):
            body = json.dumps({})
            msg = spade.message.Message(to=self.agent.env_jid, body=body, metadata={"performative": "Register"})
            await self.send(msg)

    class StepBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                # convert body to State object
                o_state = State.from_json(body['state'])

                # convert state object to nparray
                self.agent.curr_state = np.array(o_state.to_array()).astype(np.float32)

                state_in = torch.from_numpy(np.expand_dims(self.agent.curr_state, axis=0)).to(self.agent.device)
                self.agent.curr_action = self.agent.select_epsilon_greedy_action(state_in, self.agent.epsilon, self.agent.inference)

                _, self.agent.curr_action, _ = await self.agent.normative.perform('confirm_move')

                body = json.dumps({"action": int(self.agent.curr_action)})
                msg = spade.message.Message(to=self.agent.env_jid, body=body, metadata={"performative": "StepResponse"})
                await self.send(msg)
    
    class RewardBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)

                reward = body['reward']
                new_state = State.from_json(body['state'])
                new_state = np.array(new_state.to_array()).astype(np.float32)

                final_reward = reward + self.agent.penalty
                self.agent.penalty = 0

                self.agent.replay_buffer.add(self.agent.curr_state, self.agent.curr_action, final_reward, new_state)
                self.agent.curr_state = new_state

                if not self.agent.inference and len(self.agent.replay_buffer) > self.agent.batch_size:
                    states, actions, rewards, next_states = self.agent.replay_buffer.sample(self.agent.batch_size)
                    _ = self.agent.train_step(states, actions, rewards, next_states)

    
    class StopBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                if not self.agent.inference:
                    torch.save(self.agent.trgt_nn.state_dict(), f'{os.getcwd()}/weights/{self.agent.weights}.pth')
                await self.agent.stop()