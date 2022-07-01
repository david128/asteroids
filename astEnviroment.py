import asteroids
import asteroidsEasy
import asteroidsNormal

import gym
from gym import spaces
import numpy as np


class astEnv(gym.Env):

    def __init__(self):
        self.k = 1
        self.ag = self.normal()
        self.asteroidsGame = self.ag
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = self.ag
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, renderMode=True)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k

    def easy(self):
        return asteroidsEasy.AsteroidsGame()

    def normal(self):
        return asteroidsNormal.AsteroidsGame()

    def makeNormal(self):
        self.ag = self.normal

    def makeEasy(self):
        self.ag = self.easy
