# gymnasium
import gymnasium as gym
from gym import Env
from gym.spaces import Discrete, Box, Dict, Tuple, MultiBinary, MultiDiscrete

# helpers
import numpy as np
import random
import os
from enum import Enum
import random

# stable baselines3
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv


class Actions(Enum):
    RotateLeft = 0
    RotateRight = 1
    MoveLeft = 2
    MoveRight = 3
    MoveDown = 4
    Throw = 5

class PuzzlePiece():
    def __init__(self):
        self.spawn_pos = (0,5)
        self.shape = np.zeros((3,3))

    def init_pos(self):
        self.pos = [(self.spawn_pos[0] + j, self.spawn_pos[1] + i - 1) for i in range(self.shape.shape[1]) for j in range(self.shape.shape[0]) if (self.shape[j,i] == 1)]
    

    @property
    def Position(self):
        return self.pos

class Z(PuzzlePiece):
    def __init__(self):
        super().__init__()
        mirrored = random.choice((False, True))
        if mirrored:
            self.shape = np.array([[1, 1, 0],
                          [0, 1, 1]])
        else:
            self.shape = np.array([[0, 1, 1],
                          [1, 1, 0]])
        self.init_pos()

class L(PuzzlePiece):
    def __init__(self):
        super().__init__()
        mirrored = random.choice((False, True))
        if mirrored:
            self.shape = np.array([[0, 1],
                                   [0, 1],
                                   [1, 1]])
        else:
            self.shape = np.array([[1, 0],
                                   [1, 0],
                                   [1, 1]])
        self.init_pos()

class T(PuzzlePiece):
    def __init__(self):
        super().__init__()
        self.shape = np.array([[1, 1, 1],
                               [0, 1, 0]])
        self.init_pos()

class S(PuzzlePiece):
    def __init__(self):
        super().__init__()
        self.shape = np.array([[1, 1],
                               [1, 1]])
        self.init_pos()


class Board():
    def __init__(self) -> None:
        self.board = np.zeros((20,10))
        puzzle_pieces = (Z, S, T, L)
        self.active_piece = Z()
        self.locked_positions = []
        
    def lock_active_piece(self, tetromino):
        self.locked_positions.append(self.active_piece.pos)
        self.new_piece()
    
    def move_right(self):
        self.clear_board()
        for pos in self.active_piece.Position:
            if pos[0] + 1 < 0 or self.board[pos[0] + 1, pos[1]] == 1:
                return
        self.active_piece = [(position[0] + 1, position[1]) for position in self.active_piece.Position]
        self.draw_active_piece()

    def new_piece(self):
        self.active_piece = random.choice([Z(False), Z(True), L(False), L(True), T(), S()])

    def draw_active_piece(self):
        for pos in self.active_piece.Position:
            self.board[pos] = 1

    def clear_board(self):
        self.board = np.zeros((20,10))
        for pos in self.locked_positions:
            self.board[pos] = 1

    
    @property
    def State(self):
        return self.board
    


class PuzzleEnv(Env):
    def __init__(self):
        # action space 
        # rotate left | rotate right | move left | move right | move down | throw 
        self.action_space = Discrete(6)
        self.observation_space = Box(0,1, shape=(20, 10), dtype=np.int8)
        self.board = Board()
    
    def step(self, action):
        self.done = False


    def render(self, mode='human'):
        self.board.move_right()
        print(self.board.State)


    def get_state(self):
        return self.board

