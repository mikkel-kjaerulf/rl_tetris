# helpers
import os 

# environment
from environment.puzzle_env import PuzzleEnv

# stable baselines
import gymnasium as gym 
from stable_baselines3 import PPO, HER, DQN, SAC, DDPG, TD3, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_checker import check_env

env = PuzzleEnv()
env.reset()  

log_path = os.path.join('training', 'logs')

check_env(env=env, warn=True, skip_render_check=True)

model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=log_path)

print("training...")
model.learn(total_timesteps=200000)

env.close()

# save model
save_path = os.path.join("training", "saved_models", "ent_reg_001_model")
model.save(save_path)