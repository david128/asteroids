import random
import gym
import astEnviroment
import PPO_agent
import A2C_agent
import DQN_agent


from stable_baselines3 import A2C
from stable_baselines3 import DQN
from stable_baselines3 import PPO

import os
import time
import asteroidsPlayable

env = astEnviroment.AstEnv()
cEnv = astEnviroment.CurriculumEnv()
aimEnv = astEnviroment.AimEnv()
avoidEnv = astEnviroment.AvoidEnv()
rsEnv = astEnviroment.RSEnv()
hrlEnv = astEnviroment.HRLEnv()
env.setK(4)
cEnv.setK(4)
env.reset()
cEnv.reset()
rsEnv.reset()
hrlEnv.reset()
obs = env.reset()
TIMESTEPS = 25000
NUMEPISODES = 100

#asteroidsPlayable.play()

trainStandard = False
trainCur = False
trainRS = False
trainComponents = False
trainHRL = True

testRL = False

#3 standard rl
for _ in range(2):
    if trainStandard:
        #agent = A2C_agent.A2C_agent(env,"a2c")
        #agent.train(TIMESTEPS, NUMEPISODES)

        #agent = DQN_agent.DQN_agent(env,"DQN")
        #agent.train(TIMESTEPS, NUMEPISODES)

        agent = PPO_agent.PPO_agent(env,"PPO")
        agent.train(TIMESTEPS, NUMEPISODES)

for _ in range(3):
    #3 rl with cl
    if trainCur:
        agent = A2C_agent.A2C_agent(cEnv,"a2c-curriculum")
        agent.train(TIMESTEPS, NUMEPISODES)

        agent = DQN_agent.DQN_agent(cEnv,"DQN-curriculum")
        agent.train(TIMESTEPS, NUMEPISODES)

        agent = PPO_agent.PPO_agent(cEnv,"PPO-curriculum")
        agent.train(TIMESTEPS, NUMEPISODES)



    #3 irl
    if trainRS:
        agent = A2C_agent.A2C_agent(rsEnv, "a2c-rs")
        agent.train(TIMESTEPS, NUMEPISODES)

        agent = DQN_agent.DQN_agent(rsEnv, "DQN-rs")
        agent.train(TIMESTEPS, NUMEPISODES)

        agent = PPO_agent.PPO_agent(rsEnv, "PPO-rs")
        agent.train(TIMESTEPS, NUMEPISODES)

for _ in range(1):
    #train hierarchical components
    if trainComponents:
        #agent = A2C_agent.A2C_agent(avoidEnv,"a2c-avoid")
        #agent.train(TIMESTEPS, NUMEPISODES)

        #agent = A2C_agent.A2C_agent(aimEnv,"a2c-aim")
        #agent.train(TIMESTEPS, NUMEPISODES)

        #agent = DQN_agent.DQN_agent(avoidEnv,"DQN-avoid")
        #agent.train(TIMESTEPS, NUMEPISODES)

        agent = DQN_agent.DQN_agent(aimEnv,"DQN-aim")
        agent.train(TIMESTEPS, NUMEPISODES)
        for _ in range(2):
            agent = PPO_agent.PPO_agent(avoidEnv,"PPO-avoid")
            agent.train(TIMESTEPS, NUMEPISODES)

            agent = PPO_agent.PPO_agent(aimEnv,"PPO-aim")
            agent.train(TIMESTEPS, NUMEPISODES)

for _ in range(3):
    if trainHRL:

        #load component models
        a2CAvoidModel = A2C.load("models/components/a2c/avoid.zip", env=avoidEnv)
        a2cAimModel = A2C.load("models/components/a2c/aim.zip", env=aimEnv)

        hrlEnv.setModels(avoidModel=a2CAvoidModel,aimModel=a2cAimModel)
        agent = A2C_agent.A2C_agent(hrlEnv,"a2c-HRL")
        agent.train(TIMESTEPS, NUMEPISODES)

        # load component models
        dqnAvoidModel = DQN.load("models/components/DQN/avoid.zip", env=avoidEnv)
        dqnAimModel = DQN.load("models/components/DQN/aim.zip", env=aimEnv)

        hrlEnv.setModels(avoidModel=dqnAvoidModel, aimModel=dqnAimModel)
        agent = DQN_agent.DQN_agent(hrlEnv, "DQN-HRL")
        agent.train(TIMESTEPS, NUMEPISODES)

        #load component models
        ppoAvoidModel = PPO.load("models/components/PPO/avoid.zip", env=avoidEnv)
        ppoAimModel = PPO.load("models/components/PPO/aim.zip", env=aimEnv)

        hrlEnv.setModels(avoidModel=ppoAvoidModel,aimModel=ppoAimModel)
        agent = PPO_agent.PPO_agent(hrlEnv,"PPO-HRL")
        agent.train(TIMESTEPS, NUMEPISODES)

modelList =[]

if testRL:

    cwd = os.getcwd()  # Get the current working directory (cwd)

    modelList.append((A2C.load(str(cwd) + "/models/testModels/a2c/standard/850000.zip", env=env), "A2C_Standard"))
    modelList.append((DQN.load(str(cwd) + "/models/testModels/dqn/standard/1325000.zip", env=env), "DQN_Standard"))
    modelList.append((PPO.load(str(cwd) + "/models/testModels/ppo/standard/2475000.zip", env=env), "PPO_Standard"))

    modelList.append((A2C.load(str(cwd) + "/models/testModels/a2c/cur/2475000.zip", env=env), "A2C_c"))
    modelList.append((DQN.load(str(cwd) + "/models/testModels/dqn/cur/1450000.zip", env=env), "DQN_c"))
    modelList.append((PPO.load(str(cwd) + "/models/testModels/ppo/cur/2475000.zip", env=env), "PPO_c"))

    modelList.append((A2C.load(str(cwd) + "/models/testModels/a2c/rs/425000.zip", env=env), "A2C_rs"))
    modelList.append((DQN.load(str(cwd) + "/models/testModels/dqn/rs/2350000.zip", env=env), "DQN_rs"))
    modelList.append((PPO.load(str(cwd) + "/models/testModels/ppo/rs/2475000.zip", env=env), "PPO_rs"))


    #loop through models
    for m in modelList:
        print(m[1])
        #f = open(("logs/results/" + m[1] + ".csv"), "x")
        for i in range(2):
            obs = env.reset()
            done = False
            while not done:
                action, _states = m[0].predict(obs, deterministic=True)
                obs, rewards, done, info = env.step(action)
            #print result to file
            #f.write(str(env.score) + ",")
            print("ep:" + str(i) + " " + str(env.score))






