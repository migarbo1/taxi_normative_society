from collections import deque
import numpy as np
import torch

class ReplayBuffer(object):

  def __init__(self, size, device='cpu'):
    self.buffer = deque(maxlen=size)
    self.device = device

  def add(self, state, action, reward, next_state):
    self.buffer.append((state, action, reward, next_state))

  def __len__(self):
    return len(self.buffer)

  def sample(self, num_samples):
    states, actions, rewards, next_states = [], [], [], []
    idx = np.random.choice(len(self.buffer), num_samples)
    for i in idx:
      elem = self.buffer[i]
      state, action, reward, next_state = elem
      states.append(np.array(state, copy=False))
      actions.append(np.array(action, copy=False))
      rewards.append(reward)
      next_states.append(np.array(next_state, copy=False))

    states = torch.as_tensor(np.array(states), device=self.device)
    actions = torch.as_tensor(np.array(actions), device=self.device)
    rewards = torch.as_tensor(np.array(rewards, dtype=np.float32), device=self.device)
    next_states = torch.as_tensor(np.array(next_states), device=self.device)

    return states, actions, rewards, next_states