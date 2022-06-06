import random
import gym
import astEnviroment
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

model = PPO("MlpPolicy",env,verbose=1,tensorboard_log=log_dir)

TIMESTEPS =1000
for i in range(1,1000):
    model.learn(total_timesteps=TIMESTEPS,reset_num_timesteps=False,tb_log_name="PPO")
    model.save(f"logs/PPO/{TIMESTEPS*i}")


while True:
    # Take a random action
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)

    # Render the game
    env.render()

    if done == True:
        break