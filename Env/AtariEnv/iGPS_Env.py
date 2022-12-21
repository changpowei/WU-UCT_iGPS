import numpy as np
import pandas as pd
from scipy.stats import stats
import gym
from copy import deepcopy

import matlab.engine
eng = matlab.engine.start_matlab()

class iGPS_Env(gym.Env):
    def __init__(self, config):

        self.BS_num = config.BS_num
        self.height = config.height
        self.width = config.width
        self.DOP_thres = config.DOP_thres
        self.cov_thres = config.cov_thres
        self.dir_name = config.dir_name

        self._max_episode_steps = self.BS_num

        self.grid_data = np.loadtxt("data/northern_position_highist12x14.txt", dtype='float', delimiter=',')
        self.terrain_data = self.grid_data[:, 1].reshape(12, 14)
        self.terrain_data = pd.DataFrame(self.terrain_data)
        self.org_terrain = self.terrain_data.apply(stats.zscore).to_numpy()

        self.frames = np.zeros((self.BS_num + 1, self.height, self.width))
        self.frames[0] = self.org_terrain

        self.env_type = None

        self.action_space = gym.spaces.Discrete((self.height * self.width) -1)

        self.historical_action = np.zeros(self.BS_num)
        self.current_step_count = 0



    def reset(self):
        self.historical_action = np.zeros(self.BS_num)

        state = np.zeros((self.BS_num + 1, self.height, self.width))
        state[0] = self.org_terrain

        self.frames = state
        self.current_step_count = 0
        return state

    def step(self, action):
        self.historical_action[self.current_step_count] = action

        next_state = np.zeros((self.BS_num + 1, self.height, self.width))
        next_state[0] = self.org_terrain

        for i in range(0, self.current_step_count+1):
            historical_state = np.zeros((self.height, self.width))
            for j in range(0, i + 1):
                historical_state[int(self.historical_action[j] // self.width), int(self.historical_action[j] % self.width)] = 1.0
            next_state[i+1] = historical_state

        self.current_step_count += 1
        self.frames = next_state

        if self.current_step_count < self.BS_num : # not over yet
            done = False
            reward = 0
            # for n in range(1, current_step_count+1):
            #         for i in range(0, n):
            #             next_state[n, int(self.historical_action[i] // self.width),
            #                           int(self.historical_action[i] % self.width)] = 1.0

            return next_state, reward, done, self.current_step_count
        else:
            done = True
            reward = 0
            lats, lons = np.zeros(self.BS_num), np.zeros(self.BS_num)

            for i in range(self.current_step_count):
                # grid_data = np.loadtxt("data/northern_position_highist12x14.txt", dtype='float', delimiter=',')
                lats[i] = self.grid_data[int(self.historical_action[i]), 1]
                lons[i] = self.grid_data[int(self.historical_action[i]), 2]

                # if the base station is set on a grid with a height of 0, return coverage=0
                if (lats[i] == 0 or lons[i] == 0):
                    return next_state, reward, done, self.current_step_count

            lats = matlab.double(lats.tolist())
            lons = matlab.double(lons.tolist())
            # calculate dilution of precision(DOP) and coverage rate
            DOP_rate = eng.cal_DOP_northern(lats, lons, nargout=1)
            if (DOP_rate >= self.DOP_thres):
                try:
                    coverage_rate = eng.cal_coverage_rate_dipole_northern(lats, lons, nargout=1)
                except:
                    print("無法計算覆蓋率，覆蓋率設定為0")
                    coverage_rate = 0
            else:
                coverage_rate = 0

            print("save txt => DOP_rate = {}, coverage_rate = {}".format(DOP_rate, coverage_rate))
            # record pureMCTS simulation results
            f = open('simulation_result/' + self.dir_name + '/coverage_result.txt', 'a')
            f.write(str(DOP_rate) + "\\\\" + str(coverage_rate) + "\\\\" + str(lats) + str(lons) + '\n')
            f.close()
            if (coverage_rate >= self.cov_thres):
                reward = coverage_rate
            else:
                reward = 0

            return next_state, reward, done, self.current_step_count

    def clone_full_state(self):
        frame_data = self.frames.copy()
        # state_data = gym.Env.unwrapped.clone_full_state()
        # full_state_data = (state_data, frame_data)
        full_state_data = (self.historical_action, frame_data)

        return full_state_data

    def restore_full_state(self, full_state_data):
        historical_action_data, frame_data = full_state_data

        self.frames = frame_data.copy()
        self.historical_action = historical_action_data.copy()
        # gym.Env.unwrapped.restore_full_state(state_data)

    def get_state(self):
        # state = np.zeros((self.BS_num + 1, self.height, self.width))
        # state[0] = self.org_terrain
        #
        # for i in range(0, self.current_step_count):
        #     historical_state = np.zeros((self.height, self.width))
        #     for j in range(0, i + 1):
        #         historical_state[int(self.historical_action[j] // self.width), int(self.historical_action[j] % self.width)] = 1.0
        #     state[i+1] = historical_state
        return self.frames


    def render(self, mode='human'):
        return

    def close(self):
        return self.close()


