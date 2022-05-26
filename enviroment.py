import asteroids

import gym
from gym import spaces
import numpy as np


go =True



class asteroidEnv(gym.Env):

    def __init__(self):
        self.asteroidsGame = asteroids.AsteroidsGame()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(np.array([0, 0, 0, 0, 0]), np.array([10, 10, 10, 10, 10]), dtype=np.int)

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroids.AsteroidsGame()
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        self.asteroidsGame.redrawWindow()

