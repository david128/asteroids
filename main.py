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
aimEnv = astEnviroment.AimEnv()
avoidEnv = astEnviroment.AvoidEnv()
env.setK(4)
cEnv.setK(4)
env.reset()
cEnv.reset()
obs = env.reset()
TIMESTEPS = 25000
NUMEPISODES = 50

#asteroidsPlayable.play()

'''''
agent = A2C_agent.A2C_agent(cEnv,"a2c-curriculum")
agent.train(TIMESTEPS, NUMEPISODES)

agent = A2C_agent.A2C_agent(env,"a2c")
agent.train(TIMESTEPS, NUMEPISODES)

agent = DQN_agent.DQN_agent(env,"DQN")
agent.train(TIMESTEPS, NUMEPISODES)

agent = DQN_agent.DQN_agent(cEnv,"DQN-curriculum")
agent.train(TIMESTEPS, NUMEPISODES)

agent = PPO_agent.PPO_agent(cEnv,"PPO-curriculum")
agent.train(TIMESTEPS, NUMEPISODES)

agent = PPO_agent.PPO_agent(env,"PPO")
agent.train(TIMESTEPS, NUMEPISODES)
'''''

agent = A2C_agent.A2C_agent(avoidEnv,"a2c-avoid")
agent.train(TIMESTEPS, NUMEPISODES)

agent = A2C_agent.A2C_agent(aimEnv,"a2c-aim")
agent.train(TIMESTEPS, NUMEPISODES)

agent = DQN_agent.DQN_agent(avoidEnv,"DQN-avoid")
agent.train(TIMESTEPS, NUMEPISODES)

agent = PPO_agent.PPO_agent(avoidEnv,"PPO-avoid")
agent.train(TIMESTEPS, NUMEPISODES)


agent = DQN_agent.DQN_agent(aimEnv,"DQN-aim")
agent.train(TIMESTEPS, NUMEPISODES)

agent = PPO_agent.PPO_agent(aimEnv,"PPO-aim")
agent.train(TIMESTEPS, NUMEPISODES)



'''''
env.setK(1)

agent = DQN_agent.DQN_agent(env,"DQN-no-fs")
agent.train(TIMESTEPS, NUMEPISODES)

agent = A2C_agent.A2C_agent(env,"a2c-no-fs")
agent.train(TIMESTEPS, NUMEPISODES)

agent = PPO_agent.PPO_agent(env,"PPO-no-fs")
agent.train(TIMESTEPS, NUMEPISODES)
'''''






