from stable_baselines3 import DQN
import os
import time

class DQN_agent():


    def __init__(self,env):
        self.name = "DQN"
        self.models_dir = f"models/{self.name}/{self.name}-{int(time.time())}"
        self.log_dir = f"logs/{self.name}/{self.name}-{int(time.time())}"

        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.model = DQN("MlpPolicy", env, verbose=1, tensorboard_log=self.log_dir)

    def train(self,timesteps, episodes):

        for i in range(1, episodes):
            self.model.learn(total_timesteps=timesteps, reset_num_timesteps=False, tb_log_name="DQN")
            self.model.save(f"{self.models_dir}/{self.name}/{timesteps * i}")

