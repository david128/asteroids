from stable_baselines3.common.callbacks import BaseCallback


class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=1):
        super(TensorboardCallback, self).__init__(verbose)
        self.score = 0

    def _on_rollout_end(self) -> None:
        self.logger.record("score", self.score)
        self.score=0

    def _on_step(self) -> bool:
        self.score  += self.training_env.get_attr("score")[0]
        return True