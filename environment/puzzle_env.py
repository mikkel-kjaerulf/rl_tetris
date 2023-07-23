# gymnasium
import gymnasium as gym
from gymnasium import Env
from gymnasium.spaces import Discrete, Box, Dict, Tuple, MultiBinary, MultiDiscrete

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
        Nothing = 4


class PuzzlePiece():
    def __init__(self):
        self.pos = (0,5)
        self.shape = random.choice((
    np.array([[1, 1, 0],[0, 1, 1]]),
    np.array([[0, 1, 1],[1, 1, 0]]),
    np.array([[0, 1],[0 ,1],[1, 1]]),
    np.array([[1, 0],[1, 0],[1, 1]]),
    np.array([[1, 1, 1], [0, 1, 0]]),
    np.array([[1, 1], [1, 1]]),
    np.array([[1, 0], [1, 0], [1, 0]])
    ))
        self.__updatePositionShape__()

    def __updatePositionShape__(self):
        self.pos_shape = np.array([[self.pos[0] + j, self.pos[1] + i - 1] for i in range(self.shape.shape[1]) for j in range(self.shape.shape[0]) if (self.shape[j,i] == 1)])
    
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
        self.field = np.zeros((self.height,self.width), dtype=np.int8)
        self.active_piece = PuzzlePiece()
        self.locked_positions = np.array([[0,0]])
        
    def lock_active_piece(self):
        self.locked_positions = np.concatenate((self.locked_positions,self.active_piece.PositionShape))
    
    def move(self, dir) -> bool:
        move_allowed = True
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
            move_allowed = False
        self.place_active_piece()
        return move_allowed

    def rotate(self, dir):
        self.reset_board()
        if dir == 'right':
            k = 1
        elif dir == 'left':
            k = 3
        self.active_piece.__setShape__(np.rot90(self.active_piece.Shape, k=k))
        if self.check_collision() == True:
            self.active_piece.__setShape__(np.rot90(self.active_piece.Shape, k=4-k))
        self.place_active_piece()

    def check_collision(self) -> bool:
        self.reset_board()
        for pos in self.active_piece.PositionShape:
            if pos[0] >= self.height or pos[0] < 0 or pos[1] >= self.width or pos[1] < 0 or self.field[pos[0], pos[1]] == 1:
                return True
        return False
    
    def __get_locked_positions__(self):
        return self.locked_positions

    def new_piece(self) -> bool:
        self.active_piece = PuzzlePiece()
        return not self.check_collision()

    def place_active_piece(self):
        for pos in self.active_piece.PositionShape:
            self.field[pos[0], pos[1]] = 1

    def reset_board(self):
        self.field = np.zeros((self.height,self.width), dtype=np.int8)
        for pos in self.locked_positions:
            self.field[pos[0], pos[1]] = 1
    
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
            self.locked_positions = np.array([(pos[0] - len(full_lines), pos[1]) for pos in self.locked_positions if pos[0] not in full_lines])
        
        return len(full_lines)
    
    @property
    def State(self):
        return self.field

class PuzzleEnv(gym.Env):

    def __init__(self):
        # action space 
        # rotate left | rotate right | move left | move right | move down | throw 
        self.action_space = Discrete(5)
        self.observation_space = Box(low=0,high=1, shape=(20, 10), dtype=np.int8)
        self.board = Board()  # seed is not used
        self.done = False
        self.tick_rate = 30
    
    def reset(self, **kwargs):
        self.done = False
        self.board = Board()
        return (self.__get_observation__(), {})
    
    def step(self, action):
        self.done = False
        step_reward = 0
        if self.render_mode == "human":
                print("-----")
        if (action == Actions.MoveRight.value):
            self.board.move('right')
        if (action == Actions.MoveLeft.value):
            self.board.move('left')
        if (action == Actions.RotateLeft.value):
            self.board.rotate('left')
        if (action == Actions.RotateRight.value):
            self.board.rotate('right')
        if (action == Actions.Nothing.value):
            pass
        self.__render__()
        if self.board.move('down') == False:
            step_reward += 10
            self.board.lock_active_piece()
            step_reward -= self.__calculate_holes__()
            if self.render_mode == "human":
                print("step_reward after fit: ", step_reward)
            step_reward -= self.__calculate_aggregate_height__()
            if self.render_mode == "human":
                print("step_reward after height: ", step_reward)
            if self.board.new_piece() == False:
                #step_reward += len(self.board.__get_locked_positions__())
                self.done = True
        self.__render__()
        step_reward += math.pow(10, self.board.check_and_collapse_lines()) - 1
        if (self.render_mode == "human" and not step_reward == 0):
            print("final step_reward: ", step_reward)
        observation = self.__get_observation__()

        return (observation, step_reward, self.done, False, {"Step Reward": step_reward})
    
    def __calculate_reward__(self):
        # TODO create reward function that takes into account:
        # aggregate height: building flat is better
        # completed lines: sort of already fixed
            # maybe something like how big a percentage a line has been cleared?
        # holes: a bit like the below functions
        # bumpiness: sort of like building flat
        y_max = np.max(self.board.__get_locked_positions__()[:,0])
        y_min = np.min(self.board.__get_locked_positions__()[:,0])
        #x_max = np.max(self.board.__get_locked_positions__()[:,1])
        #x_min = np.min(self.board.__get_locked_positions__()[:,1])
        x_max = self.board.width -1
        x_min = 0
        return (len(self.board.__get_locked_positions__())/((y_max - y_min + 1) * (x_max - x_min + 1)))
    
    #def __calculate_percentage_of_completed_lines__(self):
    #    for x in 

    
    def __calculate_aggregate_height__(self):
        """
        Agg_height = Te sum of the height of all columns
        """
        agg_height = 0
        for x in range(0, self.board.width):
            agg_height += np.min(self.board.__get_locked_positions__()[:,0])
        return agg_height

    
    def __calculate_holes__(self) -> int:
        """
        A hole is defined as en empty space with a non-empty space above it
        """
        holes = 0
        for pos in self.board.active_piece.PositionShape:
            x = pos[1]
            for y in range (pos[0] + 1, self.board.height):
                if [y, x] in self.board.__get_locked_positions__().tolist():
                    break
                if self.board.field[y, x] == 0:
                    holes += 1
        if self.render_mode == "human":
            print("holes: ", holes)
        return holes

    def __render__(self):
        if self.render_mode == "human":
            self.screen.fill((0, 0, 0))
            for i in range(self.board.height):
                    for j in range(self.board.width):
                        if self.board.State[i, j] == 1:
                            pygame.draw.rect(self.screen, (255, 255, 255), (j * 30, i * 30, 30, 30))
            pygame.display.flip()
            self.clock.tick(self.tick_rate)
        elif self.render_mode == "terminal":
            print(self.__get_observation__())

    def render(self, render_mode="none"):
        self.render_mode = render_mode
        if self.render_mode == "human":
            pygame.init()
            self.clock = pygame.time.Clock()
            self.screen_width = self.board.width * 30
            self.screen_height = self.board.height * 30
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            self.screen.fill((0, 0, 0))
            pygame.display.set_caption("Tetris")
        
    def close(self):
        pygame.quit()

    def __get_observation__(self):
        return self.board.field


