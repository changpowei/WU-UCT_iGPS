import numpy as np
import random
import os

from Policy.PPO.PPOPolicy import PPOAtariCNN, PPOSmallAtariCNN


class PolicyWrapper():
    def __init__(self, policy_name, env_name, action_n, device):
        self.policy_name = policy_name
        self.env_name = env_name
        self.action_n = action_n
        self.device = device

        self.policy_func = None

        self.init_policy()

    def init_policy(self):
        if self.policy_name == "Random" or self.policy_name == "Modify_Random":
            self.policy_func = None

        elif self.policy_name == "PPO":
            assert os.path.exists("./Policy/PPO/PolicyFiles/PPO_" + self.env_name + ".pt"), "Policy file not found"

            self.policy_func = PPOAtariCNN(
                self.action_n,
                device = self.device,
                checkpoint_dir = "./Policy/PPO/PolicyFiles/PPO_" + self.env_name + ".pt"
            )

        elif self.policy_name == "DistillPPO":
            assert os.path.exists("./Policy/PPO/PolicyFiles/PPO_" + self.env_name + ".pt"), "Policy file not found"
            assert os.path.exists("./Policy/PPO/PolicyFiles/SmallPPO_" + self.env_name + ".pt"), "Policy file not found"

            full_policy = PPOAtariCNN(
                self.action_n,
                device = "cpu", # To save memory
                checkpoint_dir = "./Policy/PPO/PolicyFiles/PPO_" + self.env_name + ".pt"
            )

            small_policy = PPOSmallAtariCNN(
                self.action_n,
                device = self.device,
                checkpoint_dir = "./Policy/PPO/PolicyFiles/SmallPPO_" + self.env_name + ".pt"
            )

            self.policy_func = [full_policy, small_policy]
        else:
            raise NotImplementedError()

    def get_action(self, state):
        if self.policy_name == "Random":
            return random.randint(0, self.action_n - 1)
        elif self.policy_name == "PPO":
            return self.categorical(self.policy_func.get_action(state))
        elif self.policy_name == "DistillPPO":
            return self.categorical(self.policy_func[1].get_action(state))

        elif self.policy_name == "Modify_Random":
            moved_index = np.zeros([self.action_n], dtype=np.float32)
            for i in range(state.shape[0] - 1, 0, -1):
                if state[i].any():
                    moved_action = np.where(state[i] == 1)
                    for j in range(moved_action[0].size):
                        moved_index[moved_action[0][j] * state.shape[1] + moved_action[1][j]] = 1
                    break
            while True:
                action = random.randint(0, self.action_n - 1)
                if moved_index[action] != 1:
                    return action
        else:
            raise NotImplementedError()

    def get_value(self, state):
        if self.policy_name == "Random" or self.policy_name == "Modify_Random":
            return 0.0
        elif self.policy_name == "PPO":
            return self.policy_func.get_value(state)
        elif self.policy_name == "DistillPPO":
            return self.policy_func[0].get_value(state)
        else:
            raise NotImplementedError()

    def get_prior_prob(self, state):
        if self.policy_name == "Random":
            return np.ones([self.action_n], dtype = np.float32) / self.action_n
        elif self.policy_name == "PPO":
            return self.policy_func.get_action(state)
        elif self.policy_name == "DistillPPO":
            return self.policy_func[0].get_action(state)

        elif self.policy_name == "Modify_Random":

            percentage = np.ones([self.action_n], dtype=np.float32)

            for i in range(state.shape[0] - 1, 0, -1):
                if state[i].any():
                    percentage = percentage / (self.action_n - i)
                    moved_action = np.where(state[i] == 1)
                    for j in range(moved_action[0].size):
                        percentage[moved_action[0][j] * state.shape[1] + moved_action[1][j]] = 0
                    return percentage

            return percentage / self.action_n
        else:
            raise NotImplementedError()

    @staticmethod
    def categorical(probs):
        val = random.random()
        chosen_idx = 0

        for prob in probs:
            val -= prob

            if val < 0.0:
                break

            chosen_idx += 1

        if chosen_idx >= len(probs):
            chosen_idx = len(probs) - 1

        return chosen_idx
