import asteroids
import asteroidsEasy

import gym
from gym import spaces
import numpy as np


class asteroidEnv(gym.Env):

    k=4

    def __init__(self):
        self.asteroidsGame = asteroidsEasy.AsteroidsGame()
        self.action_space = spaces.Discrete(12)
        self.observation_space = spaces.Box(low=-1000,high=1000,shape=(261,),dtype=np.float32)

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame()
        obs = self.asteroidsGame.getGridObservation()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action,k=self.k,renderMode=True)
        obs = self.asteroidsGame.getGridObservation()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        #render now in action
        #self.asteroidsGame.redrawWindow()
        pass

