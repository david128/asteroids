import random
import gym
import astEnviroment
import PPO_agent
import A2C_agent
import DQN_agent
from stable_baselines3 import PPO
import os
import time
import asteroidsPlayable

env = astEnviroment.asteroidEnv()
env.reset()
obs = env.reset()
TIMESTEPS = 1000
NUMEPISODES = 1000
# not DDPG not SAC not TD3

agent = A2C_agent.A2C_agent(env,"A2C-Easy")
agent.train(TIMESTEPS, NUMEPISODES)


#asteroidsPlayable.play()