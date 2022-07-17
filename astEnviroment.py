import asteroids
import asteroidsEasy
import asteroidsNormal

import gym
from gym import spaces
import numpy as np


class AstEnv(gym.Env):

    def __init__(self):
        self.k = 1
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(0)
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(0)
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


class CurriculumEnv(gym.Env):

    def __init__(self):
        self.k = 1
        self.s = 1
        self.tR = 0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(1)
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)

    def reset(self):
        if self.s == 1 and self.tR > 1000:
            self.s=0
            print("Change to harder")
        self.tR=0
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(self.s)
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, renderMode=True)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        self.tR +=reward
        done = self.asteroidsGame.is_done()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k