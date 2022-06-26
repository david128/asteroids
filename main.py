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
TIMESTEPS = 25000
NUMEPISODES = 100
# not DDPG not SAC not TD3


#asteroidsPlayable.play()

agent = PPO_agent.PPO_agent(env,"PPO-norm")
agent.train(TIMESTEPS, NUMEPISODES)

model = PPO.load("models/PPO/PPO-incrDist-1656002278/PPO-incrDist/875000.zip",env=env)
for i in range(NUMEPISODES):
    obs = env.reset()
    done = False
    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, done, info = env.step(action)



