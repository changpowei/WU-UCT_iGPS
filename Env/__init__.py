from gym.envs.registration import register
import gym
from .types import Config
import argparse
parser = argparse.ArgumentParser()

V0NAME = 'iGPS'

parser.add_argument(
    "--BS_num",
    type=int,
    default=4,
)

parser.add_argument(
    "--height",
    type=int,
    default=12,
)

parser.add_argument(
    "--width",
    type=int,
    default=14,
)

parser.add_argument(
    "--DOP_thres",
    type=int,
    default=70,
)

parser.add_argument(
    "--cov_thres",
    type=int,
    default=70,
)

parser.add_argument(
    "--dir_name",
    type=str,
    default='0408_test',
)

args = parser.parse_args()
if V0NAME not in gym.envs.registry.env_specs:

    register(
        id = 'iGPS-v1',
        entry_point = 'Env.AtariEnv:iGPS_Env',
        kwargs={'config':Config(
            BS_num = args.BS_num,
            height = args.height,
            width = args.width,
            DOP_thres = args.DOP_thres,
            cov_thres = args.cov_thres,
            dir_name = args.dir_name
        )}
    )
