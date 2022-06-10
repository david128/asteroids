import asteroids

import gym
from gym import spaces
import numpy as np


class asteroidEnv(gym.Env):

    def __init__(self):
        self.asteroidsGame = asteroids.AsteroidsGame()
        self.action_space = spaces.Discrete(12)
        self.observation_space = spaces.Box(low=0, high=255, shape=(
            asteroids.screenW, asteroids.screenH, 3), dtype=np.uint8)

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroids.AsteroidsGame()
        obs = self.asteroidsGame.getState()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action)
        obs = self.asteroidsGame.getState()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        self.render()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        self.asteroidsGame.redrawWindow()

