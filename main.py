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

#test test
#agent = PPO_agent.PPO_agent(env,"PPO-Grid-1")
#agent.train(TIMESTEPS, NUMEPISODES)

model = PPO.load("models/import/200000.zip",env=env)
for i in range(NUMEPISODES):
    obs = env.reset()
    done = False
    while not done:
        action, _states = model.predict(obs, deterministic=True)
        print(str(action) + " " +  str(_states))
        obs, rewards, done, info = env.step(action)


