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

env = astEnviroment.AstEnv()
cEnv = astEnviroment.CurriculumEnv()
env.setK(4)
cEnv.setK(4)
env.reset()
cEnv.reset()
obs = env.reset()
TIMESTEPS = 10000
NUMEPISODES = 100

#asteroidsPlayable.play()
'''
agent = DQN_agent.DQN_agent(env,"De")
agent.train(TIMESTEPS, NUMEPISODES)

agent = DQN_agent.DQN_agent(cEnv,"DeleteMe")
agent.train(TIMESTEPS, NUMEPISODES)

agent = A2C_agent.A2C_agent(env,"a2c-norm-l")
agent.train(TIMESTEPS, NUMEPISODES)

agent = PPO_agent.PPO_agent(env,"PPO-norm-l")
agent.train(TIMESTEPS, NUMEPISODES)
'''
model = PPO.load("models/import/300000.zip",env=cEnv)
for i in range(NUMEPISODES):
    obs = cEnv.reset()
    done = False
    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, done, info = cEnv.step(action)



