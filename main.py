import argparse
import multiprocessing
import scipy.io as sio
import os

from Tree.WU_UCT import WU_UCT
from Tree.UCT import UCT

from Utils.NetworkDistillation.Distillation import train_distillation


def main():
    parser = argparse.ArgumentParser(description = "P-MCTS")
    parser.add_argument("--model", type = str, default = "WU-UCT",
                        help = "Base MCTS model WU-UCT/UCT (default: WU-UCT)")

    parser.add_argument("--env-name", type = str, default = "iGPS-v1",
                        help = "Environment name (default: PongNoFrameskip-v0、iGPS-v1)")

    parser.add_argument("--MCTS-max-steps", type = int, default = 1000,
                        help = "Max simulation step of MCTS (default: 500、1000)")
    parser.add_argument("--MCTS-max-depth", type = int, default = 10,
                        help = "Max depth of MCTS simulation (default: 100、10)")
    parser.add_argument("--MCTS-max-width", type = int, default = 200,
                        help = "Max width of MCTS simulation (default: 20、200)")

    parser.add_argument("--gamma", type = float, default = 0.99,
                        help = "Discount factor (default: 1.0)")

    parser.add_argument("--expansion-worker-num", type = int, default = 1,
                        help = "Number of expansion workers (default: 1)")
    parser.add_argument("--simulation-worker-num", type = int, default = 2,
                        help = "Number of simulation workers (default: 16)")

    parser.add_argument("--seed", type = int, default = 124,
                        help = "random seed (default: 123)")

    parser.add_argument("--max-episode-length", type = int, default = 100000,
                        help = "Maximum episode length (default: 100000)")

    parser.add_argument("--policy", type = str, default = "Modify_Random",
                        help = "Prior prob/simulation policy used in MCTS Random/PPO/DistillPPO/Modify_Random (default: Random)")

    parser.add_argument("--device", type = str, default = "cuda",
                        help = "PyTorch device, if entered 'cuda', use cuda device parallelization (default: cpu)")

    parser.add_argument("--record-video", default = False, action = "store_true",
                        help = "Record video if supported (default: False)")

    parser.add_argument("--mode", type = str, default = "MCTS",
                        help = "Mode MCTS/Distill (default: MCTS)")

    args = parser.parse_args()

    env_params = {
        "env_name": args.env_name,
        "max_episode_length": args.max_episode_length
    }

    if args.mode == "MCTS":
        # Model initialization
        if args.model == "WU-UCT":
            MCTStree = WU_UCT(env_params, args.MCTS_max_steps, args.MCTS_max_depth,
                              args.MCTS_max_width, args.gamma, args.expansion_worker_num,
                              args.simulation_worker_num, policy = args.policy,
                              seed = args.seed, device = args.device,
                              record_video = args.record_video)
        elif args.model == "UCT":
            MCTStree = UCT(env_params, args.MCTS_max_steps, args.MCTS_max_depth,
                           args.MCTS_max_width, args.gamma, policy = args.policy, seed = args.seed, device = args.device)
        else:
            raise NotImplementedError()

        accu_reward, rewards, times = MCTStree.simulate_trajectory()
        print(accu_reward)

        with open("Results/" + args.model + ".txt", "a+") as f:
            f.write("Model: {}, env: {}, result: {}, MCTS max steps: {}, policy: {}, worker num: {}".format(
                args.model, args.env_name, accu_reward, args.MCTS_max_steps, args.policy, args.simulation_worker_num
            ))

        if not os.path.exists("OutLogs/"):
            try:
                os.mkdir("OutLogs/")
            except:
                pass

        sio.savemat("OutLogs/" + args.model + "_" + args.env_name + "_" + str(args.seed) + "_" + 
                    str(args.simulation_worker_num)  + ".mat",
                    {"rewards": rewards, "times": times})

        MCTStree.close()

    elif args.mode == "Distill":
        train_distillation(args.env_name, args.device)


if __name__ == "__main__":
    # Mandatory for Unix/Darwin
    multiprocessing.set_start_method("forkserver")

    main()
