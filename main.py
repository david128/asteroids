import random
import gym
import astEnviroment
import PPO_agent
import DQN_agent
from stable_baselines3 import PPO
import os
import time

env = astEnviroment.asteroidEnv()
env.reset()
obs = env.reset()
TIMESTEPS =1000

dqn = DQN_agent.DQN_agent(env)
dqn.train(TIMESTEPS, 1000)



