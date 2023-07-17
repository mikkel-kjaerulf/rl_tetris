# helpers
import os 

# environment
from env.src.puzzle_env import PuzzleEnv

# stable baselines
import gymnasium as gym 
from stable_baselines3 import PPO 
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy

env = PuzzleEnv()
env.reset()

# play around with environment
episodes = 5
for episode in range(1, episodes+1):
    obs = env.reset() # initial set of observations
    done = False
    score = 0
    while not done:
        env.render()
        action = env.action_space.sample()  # random action
        obs, reward, done, info = env.step(action)
        score += reward
    print('Episode:{} Score:{}'.format(episode, score))
env.close()