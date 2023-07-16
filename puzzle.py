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



class PuzzlePiece():
    def __init__(self):
        self.pos = (0,5)
        self.shape = random.choice((
    np.array([[1, 1, 0],[0, 1, 1]]),
    np.array([[0, 1, 1],[1, 1, 0]]),
    np.array([[0, 1],[0 ,1],[1, 1]]),
    np.array([[1, 0],[1, 0],[1, 1]]),
    np.array([[1, 1, 1], [0, 1, 0]]),
    np.array([[1, 1], [1, 1]])))
        self.__updatePositionShape__()

    def __updatePositionShape__(self):
        self.pos_shape = np.array([(self.pos[0] + j, self.pos[1] + i - 1) for i in range(self.shape.shape[1]) for j in range(self.shape.shape[0]) if (self.shape[j,i] == 1)])
    
    def __updatePosition__(self, newposition):
        self.pos_shape = newposition
        self.__updatePositionShape__()

    @property
    def Position(self):
        return self.pos
    
    @property
    def PositionShape(self):
        return self.pos_shape


class Board():

    def __init__(self) -> None:
        self.height = 20
        self.width = 10
        self.board = np.zeros((self.height,self.width))
        self.active_piece = PuzzlePiece()
        self.locked_positions = []
        
    def lock_active_piece(self, tetromino):
        self.locked_positions.append(self.active_piece.pos)
        self.new_piece()
    
    def move_right(self):
        self.reset_board()
        for pos in self.active_piece.PositionShape:
            if self.board[pos[0], pos[1] + 1] == 1:
                return
        self.active_piece.__updatePosition__((self.active_piece.Position[0], self.active_piece.Position[1] + 1))
        self.place_active_piece()
    
    def move_left(self):
        self.reset_board()
        for pos in self.active_piece.PositionShape:
            if self.board[pos[0], pos[1] - 1] == 1 or pos[1] - 1 < 0:
                return
        self.active_piece.__setpos__(np.array([(position[0], position[1] - 1) for position in self.active_piece.Position]))
        self.place_active_piece()
    
    def move_down(self):
        self.reset_board()
        for pos in self.active_piece.PositionShape:
            if self.board[pos[0] + 1, pos[0]] == 1 or pos[0] + 1 >= self.height:
                return
        self.active_piece.__setpos__([(position[0] + 1, position[1]) for position in self.active_piece.Position])
        self.place_active_piece()
    
    def rotate_right(self):
        self.reset_board()
        self.active_piece.__setpos__ = np.array([])
        self.place_active_piece()


    def new_piece(self):
        self.active_piece = PuzzlePiece()

    def place_active_piece(self):
        for pos in self.active_piece.Position:
            self.board[pos] = 1

    def reset_board(self):
        self.board = np.zeros((20,10))
        for pos in self.locked_positions:
            self.board[pos] = 1
    
    @property
    def State(self):
        return self.board
    


class PuzzleEnv(Env):

    class Actions(Enum):
        RotateLeft = 0
        RotateRight = 1
        MoveLeft = 2
        MoveRight = 3
        MoveDown = 4
        Throw = 5


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
        self.board.move_right()
        print(self.board.State)


    def get_state(self):
        return self.board

