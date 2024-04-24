from state import State
from enum import Enum
import numpy as np
import random


class GridZones(Enum):
    BARRIERS = -1
    QUEUE = 1
    CAR = 3
    PICKUP = 10
    DROP1 = 90
    DROP2 = 60
    DROP3 = 50


class Action(Enum):
    WAIT = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class TaxiGridEnv():

    def __init__(self):
        self.grid = np.zeros((8,12))
        self.drivers_dict = {}
        self._setup_grid()
        self.__invariant_grid = self.grid.copy()


    def _setup_grid(self):
        self._set_queue()
        self._set_pickup()
        self._set_drop_zones()
        self._set_barriers()


    def _set_queue(self):
        self.grid[1:-1, 0] = GridZones.QUEUE.value


    def _set_pickup(self):
        self.grid[-1, 0] = GridZones.PICKUP.value


    def _set_drop_zones(self):
        self.grid[-1, 11] = GridZones.DROP1.value
        self.grid[-1, 6] = GridZones.DROP2.value
        self.grid[3, 7] = GridZones.DROP3.value


    def _set_barriers(self):
        self.grid[1:4, 2] = GridZones.BARRIERS.value
        self.grid[5:7, 2] = GridZones.BARRIERS.value

        self.grid[1, 5:9] = GridZones.BARRIERS.value
        self.grid[3, 4:6] = GridZones.BARRIERS.value

        self.grid[5, -3:] = GridZones.BARRIERS.value

        self.grid[1:3, -1] = GridZones.BARRIERS.value

        self.grid[6:, 5] = GridZones.BARRIERS.value


    def reset(self):
        self.__init__()


    def register_driver(self):
        pos_code = GridZones.BARRIERS.value

        while pos_code != 0 and pos_code != 3:
            x = random.randint(0, self.grid.shape[0] - 1)
            y = random.randint(0, self.grid.shape[1] - 1)
            pos_code = self.grid[x,y]

        self.grid[x,y] = GridZones.CAR.value

        state = State(x, y)
        state.update_car_view(self.grid)

        return state


    def step(self, state: State, action: Action):
        action = Action(action)
        if action == Action.WAIT:
            if self.car_in_queue(state.pos) and self.next_queue_spot_occupied(state.pos):
                return 0, state
            else:
                return -100, state

        # check bounbaries for each movement action
        if action == Action.UP:
            x = state.pos[0] - 1
            if x < 0 or self.grid[x, state.pos[1]] == -1 or self.grid[x, state.pos[1]] == 3:
                return -3, state
            new_state = State(x, state.pos[1])

        if action == Action.DOWN:
            x = state.pos[0] + 1
            if x > self.grid.shape[0] - 1 or self.grid[x, state.pos[1]] == -1 or self.grid[x, state.pos[1]] == 3:
                return -3, state
            new_state = State(x, state.pos[1])

        if action == Action.LEFT:
            y = state.pos[1] - 1
            if y < 0 or self.grid[state.pos[0], y] == -1 or self.grid[state.pos[0], y] == 3:
                return -3, state
            new_state = State(state.pos[0], y)

        if action == Action.RIGHT:
            y = state.pos[1] + 1
            if y > self.grid.shape[1] - 1 or self.grid[state.pos[0], y] == -1 or self.grid[state.pos[0], y] == 3:
                return -3, state
            new_state = State(state.pos[0], y)

        reward = -1

        if self.car_in_queue(new_state.pos):
            reward = -0.5

        # If movement is possible, compute reward
        new_state.client_on_board = state.client_on_board
        if self.car_in_pick_position(new_state.pos) and new_state.client_on_board == 0:
            new_state.client_on_board = 1
            reward = 1 if reward != -90 else -90

        if self.car_in_drop_position(new_state.pos) and new_state.client_on_board == 1:
            new_state.client_on_board = 0
            reward = self.get_drop_reward(new_state.pos)
        self.update_grid(state.pos, new_state.pos)
        new_state.update_car_view(self.grid)

        return reward, new_state


    def agent_outside_queue(self, state):
        return state.pos[1] != 0


    def car_in_queue(self, pos):
        x, y = pos[0], pos[1]
        return self.grid[x, y] == GridZones.QUEUE.value or self.grid[x, y] == GridZones.PICKUP.value


    def next_queue_spot_occupied(self, pos):
        x, y = pos[0]+1, pos[1]
        return self.grid[x, y] == GridZones.CAR.value


    def car_in_pick_position(self, pos):
        x, y = pos[0], pos[1]
        return self.grid[x, y] == GridZones.PICKUP.value


    def car_in_drop_position(self, pos):
        x, y = pos[0], pos[1]
        return self.grid[x, y] == GridZones.DROP1.value or self.grid[x,y] == GridZones.DROP2.value or self.grid[x,y] == GridZones.DROP3.value


    def get_drop_reward(self, pos):
        x, y = pos[0], pos[1]
        return self.grid[x, y]


    def update_grid(self, old_pos, new_pos):
        x, y = old_pos
        x_, y_ = new_pos

        self.grid[x, y] = self.__invariant_grid[x, y]
        self.grid[x_, y_] = GridZones.CAR.value
        print(self.grid)