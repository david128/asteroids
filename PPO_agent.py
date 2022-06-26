from stable_baselines3 import PPO
import os
import time

class PPO_agent():

    def __init__(self,env,name):
        self.name = name
        self.modelName ="PPO"
        self.models_dir = f"models/{self.modelName}/{self.name}-{int(time.time())}"
        self.log_dir = f"logs/{self.modelName}/{self.name}-{int(time.time())}"

        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=self.log_dir)

    def train(self,timesteps, episodes):

        for i in range(1, episodes):
            print("Episode:" + str(i))
            self.model.learn(total_timesteps=timesteps, reset_num_timesteps=False, tb_log_name=self.name)
            self.model.save(f"{self.models_dir}/{self.name}/{timesteps * i}")

