import numpy as np

class State():

    def __init__(self, x, y):
        self.pos = [x, y]
        self.client_on_board = 0
        self.view = np.zeros((8,))


    def update_car_view(self, grid):

        ul = grid[self.pos[0]-1, self.pos[1]-1] if self.pos[0] > 0 and self.pos[1] > 0 else -1
        u = grid[self.pos[0]-1, self.pos[1]] if self.pos[0] > 0 else -1
        ur = grid[self.pos[0]-1, self.pos[1]+1] if self.pos[0] > 0 and self.pos[1] < grid.shape[1]-1 else -1

        l = grid[self.pos[0], self.pos[1]-1] if self.pos[1] > 0 else -1
        r = grid[self.pos[0], self.pos[1]+1] if self.pos[1] < grid.shape[1]-1 else -1

        dl = grid[self.pos[0]+1, self.pos[1]-1] if self.pos[0] < grid.shape[0]-1 and self.pos[1] > 0 else -1
        d = grid[self.pos[0]+1, self.pos[1]] if self.pos[0] < grid.shape[0]-1 else -1
        dr = grid[self.pos[0]+1, self.pos[1]+1] if self.pos[0] < grid.shape[0]-1 and self.pos[1] < grid.shape[1]-1 else -1

        self.view = [ul, u, ur, l, r, dl, d, dr]


    def __str__(self) -> str:
        return f'pos: {self.pos}, client_on_board: {self.client_on_board}, view: {self.view}'


    def __eq__(self, __value: object) -> bool:
        return self.pos == __value.pos and self.client_on_board == __value.client_on_board and self.view == __value.view


    def __hash__(self) -> int:
        return hash((self.pos[0], self.pos[1], self.client_on_board, *self.view))


    def to_array(self) -> list:
      return [*self.pos, self.client_on_board, *self.view]


    @staticmethod
    def to_json(state):
        sd = {}
        sd['pos'] = state.pos
        sd['client_on_board'] = state.client_on_board
        sd['view'] = list(state.view)
        return sd


    @staticmethod
    def from_json(s: dict):
        state = State(*s['pos'])
        state.client_on_board = s['client_on_board']
        state.view = s['view']
        return state


class SimpleState(State):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.view = np.zeros((4,))


    def update_car_view(self, grid):

        u = grid[self.pos[0]-1, self.pos[1]] if self.pos[0] > 0 else -1

        l = grid[self.pos[0], self.pos[1]-1] if self.pos[1] > 0 else -1
        r = grid[self.pos[0], self.pos[1]+1] if self.pos[1] < grid.shape[1]-1 else -1

        d = grid[self.pos[0]+1, self.pos[1]] if self.pos[0] < grid.shape[0]-1 else -1

        self.view = [u, d, l, r]

    @staticmethod
    def from_json(s: dict):
        state = SimpleState(*s['pos'])
        state.client_on_board = s['client_on_board']
        state.view = s['view']
        return state


def array_to_state(array):
    state = State(*array[0:2])
    state.client_on_board = array[2]
    state.view = np.array(*array[3:])
    return state