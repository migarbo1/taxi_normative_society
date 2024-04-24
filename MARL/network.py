import torch.nn.functional as F
import torch.nn as nn


class DQN(nn.Module):
  def __init__(self, num_features, num_actions):
    super(DQN, self).__init__()
    self.input_l = nn.Linear(num_features, 32)
    self.hidden_l = nn.Linear(32, 32)
    self.output_l = nn.Linear(32, num_actions)

  def forward(self, states):
    x = F.relu(self.input_l(states))
    x = F.relu(self.hidden_l(x))
    return self.output_l(x)