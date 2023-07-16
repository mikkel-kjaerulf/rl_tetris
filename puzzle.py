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
import pygame
import math

# stable baselines3
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

class Actions(Enum):
        RotateLeft = 0
        RotateRight = 1
        MoveLeft = 2
        MoveRight = 3
        MoveDown = 4
        Nothing = 5


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
        self.pos = newposition
        self.__updatePositionShape__()
    
    def __setShape__(self, newshape):
        self.shape = newshape
        self.__updatePositionShape__()

    @property
    def Position(self):
        return self.pos
    
    @property
    def PositionShape(self):
        return self.pos_shape
    
    @property
    def Shape(self):
        return self.shape


class Board():
    def __init__(self) -> None:
        self.height = 20
        self.width = 10
        self.field = np.zeros((self.height,self.width))
        self.active_piece = PuzzlePiece()
        self.locked_positions = []
        
    def lock_active_piece(self, tetromino):
        self.locked_positions.append(self.active_piece.PositionShape)
        self.new_piece()
    
    def move(self, dir):
        if dir == 'right':
            direction = (0, 1)
        elif dir == 'left':
            direction = (0, -1)
        elif dir == 'down':
            direction = (1, 0)
        self.reset_board()
        self.active_piece.__updatePosition__(tuple(map(lambda i, j: i + j, self.active_piece.Position, direction)))
        if self.check_collision() == True:
            self.active_piece.__updatePosition__(tuple(map(lambda i, j: i - j, self.active_piece.Position, direction)))
        self.place_active_piece()
    
    def rotate(self, dir):
        self.reset_board()
        if dir == 'right':
            k = 1
        elif dir == 'left':
            k = 3
        self.active_piece.__setShape__(np.rot90(self.active_piece.Shape, k=k))
        if self.check_collision() == True:
            self.active_piece.__setShape__(np.rot(self.active_piece.Shape, k=4-k))
        self.place_active_piece()

    def check_collision(self) -> bool:
        for pos in self.active_piece.PositionShape:
            if self.field[pos[0], pos[0]] == 1 or pos[0]>= self.height or pos[0] < 0 or pos[1] >= self.height or pos[1] < 0:
                return True
        return False

    def new_piece(self) -> bool:
        self.active_piece = PuzzlePiece()
        return self.check_collision()

    def place_active_piece(self):
        for pos in self.active_piece.PositionShape:
            self.field[pos[0], pos[1]] = 1

    def reset_board(self):
        self.field = np.zeros((20,10))
        for pos in self.locked_positions:
            self.field[pos] = 1
    
    def check_and_collapse_lines(self) -> int:
        full_lines = []
        for i in range(self.height):
            if np.all(self.field[i, :] == 1):
                full_lines.append(i)

        if full_lines:
            # Remove the full lines and shift the upper lines down
            self.field = np.delete(self.field, full_lines, axis=0)
            new_lines = np.zeros((len(full_lines), self.width))
            self.field = np.concatenate((new_lines, self.field), axis=0)
            self.locked_positions = [(pos[0] + len(full_lines), pos[1]) for pos in self.locked_positions]
        
        return len(full_lines) / self.width
    
    @property
    def State(self):
        return self.field
    


class PuzzleEnv(Env):

    def __init__(self):
        # action space 
        # rotate left | rotate right | move left | move right | move down | throw 
        self.action_space = Discrete(6)
        self.observation_space = Box(0,1, shape=(20, 10), dtype=np.int8)
        self.board = Board()
        self.done = False
    
    def reset(self):
        self.done = False
        self.board = Board()
    
    def step(self, action):
        step_reward = 0
        if (action == Actions.MoveRight.value):
            self.board.move('right')
        if (action == Actions.MoveLeft.value):
            self.board.move('left')
        if (action == Actions.RotateLeft.value):
            self.board.rotate('left')
        if (action == Actions.RotateRight.value):
            self.board.rotate('right')

        self.board.move('down')

        if self.board.check_collision() == True:
            self.board.lock_active_piece()
            step_reward += 1
            if self.board.new_piece() == True:
                self.done = True
        
        step_reward += math.pow(10, self.board.check_and_collapse_lines())
        observation = self.get_state()

        return observation, step_reward, self.done, {"Step Reward": step_reward}

    def render(self, render_mode='t'):
        if render_mode == 'human':
            pygame.init()
            clock = pygame.time.Clock()
            screen_width = self.board.width * 30
            screen_height = self.board.height * 30
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Tetris")

            done = False
            while not done:
                screen.fill((0, 0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                        break

                self.board.move('right')
                self.board.move('down')
                self.board.move('down')
                self.board.rotate('left')
                
                for i in range(self.board.height):
                    for j in range(self.board.width):
                        if self.board.State[i, j] == 1:
                            pygame.draw.rect(screen, (255, 255, 255), (j * 30, i * 30, 30, 30))

                pygame.display.flip()
                clock.tick(30)  # Adjust the frame rate if needed

            pygame.quit()
        else:
            self.board.move('right')
            self.board.move('down')
            self.board.move('down')
            self.board.rotate('left')
            print(self.board.State)

    def get_state(self):
        return self.board.field

