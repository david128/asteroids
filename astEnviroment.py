
import asteroidsEasy


import gym
from gym import spaces
import numpy as np

from stable_baselines3 import A2C
from stable_baselines3 import DQN
from stable_baselines3 import PPO


class AstEnv(gym.Env):

    def __init__(self, do_render):
        self.k = 4
        self.score = 0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(0)
        self.action_space = spaces.Discrete(12)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)
        self.do_render = do_render

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(0)
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, alwaysRender=self.do_render)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        self.score = self.asteroidsGame.score
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k


class CurriculumEnv(gym.Env):

    def __init__(self, do_render):
        self.k = 4
        self.s = 1
        self.tR = 0
        self.score = 0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(1)
        self.action_space = spaces.Discrete(12)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)
        self.do_render = do_render

    def reset(self):
        self.tR=0
        self.asteroidsGame.resetGame()
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, renderMode=True)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        self.tR +=reward
        done = self.asteroidsGame.is_done()
        self.score = self.asteroidsGame.score
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k


class AvoidEnv(gym.Env ):

    def __init__(self, do_render):
        self.k = 4
        self.score = 0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(2)
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)
        self.do_render = do_render

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(2)
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, renderMode=True)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        self.score = self.asteroidsGame.score
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k


class AimEnv(gym.Env):

    def __init__(self, do_render):
        self.k = 4
        self.score =0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(3)
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)
        self.do_render = do_render

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(3)
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, renderMode=True)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        self.score = self.asteroidsGame.score
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k


class RSEnv(gym.Env):

    def __init__(self, do_render):
        self.k = 4
        self.score =0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(4)
        self.action_space = spaces.Discrete(12)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)
        self.do_render = do_render

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(4)
        obs = self.asteroidsGame.observe()
        return obs

    def step(self, action):
        self.asteroidsGame.action(action, k=self.k, renderMode=True)
        obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        self.score =self.asteroidsGame.score
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k

class HRLEnv(gym.Env):




    def __init__(self, do_render):
        self.obs = None
        self.k = 4
        self.score =0
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(0)
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=-0, high=1, shape=(21,), dtype=np.float32)
        self.do_render = do_render

        #components
        avoidEnv = AvoidEnv(self.do_render)
        aimEnv = AimEnv(self.do_render)
        self.avoidModel = None
        self.aimModel = None

    def setModels(self, aimModel, avoidModel):
        self.avoidModel=avoidModel
        self.aimModel=aimModel

    def reset(self):
        del self.asteroidsGame
        self.asteroidsGame = asteroidsEasy.AsteroidsGame(0)
        self.obs = self.asteroidsGame.observe()
        return self.obs

    def step(self, action):

        avoidAction, _states = self.avoidModel.predict(self.obs, deterministic=True)
        aimAction, _states = self.aimModel.predict(self.obs, deterministic=True)

        #try to aggregate decision
        agg = self.actionAggregator(aimAction,avoidAction)
        #if agg != -1:
            #self.asteroidsGame.action(agg, k=self.k, renderMode=True)
        #HRL decides to aim or avoid
        if action ==0:
            self.asteroidsGame.hrlAction(False, avoidAction, k=self.k, renderMode=self.do_render)
        else:
            self.asteroidsGame.hrlAction(True, aimAction, k=self.k, renderMode=self.do_render)

        self.obs = self.asteroidsGame.observe()
        reward = self.asteroidsGame.evaluate()
        done = self.asteroidsGame.is_done()
        self.score =self.asteroidsGame.score
        return self.obs, reward, done, {}

    def render(self, mode="human", close=False):
        # render now in action
        # self.asteroidsGame.redrawWindow()
        pass

    def setK(self,k):
        self.k = k

    def actionAggregator(self, aim, avoid):
        action = 0
        agree = True
        if aim == 0:
            if avoid == 3:
                action = 3
            else:
                agree = False
        elif aim == 1:
            if avoid == 4:
                action = 4
            else:
                agree = False
        elif aim == 2:
            if avoid == 5:
                action = 10
        if agree:
            return action
        else:
            return -1


