import random
import gym
import astEnviroment
import PPO_agent
import DQN_agent
from stable_baselines3 import PPO
import os
import time


models_dir = f"models/PPO-{int(time.time())}"
log_dir = f"logs/PPO-{int(time.time())}"

if  not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

env = astEnviroment.asteroidEnv()
env.reset()
obs = env.reset()
TIMESTEPS =1000

dqn = DQN_agent.DQN_agent(env)
dqn.train(TIMESTEPS, 1000)



