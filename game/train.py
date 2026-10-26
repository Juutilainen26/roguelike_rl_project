import os
import sys

sys.path.append(os.path.dirname(__file__))

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from rogue_env import RogueEnv
from stable_baselines3.common.callbacks import CheckpointCallback

TOTAL_TIMESTEPS=3_300_000# 왜 언더바가 들어가는거지?
MODEL_PATH=os.path.join(os.path.dirname(__file__), "rogue_ppo")

def main():
    env=Monitor(RogueEnv())

    model=PPO("MlpPolicy", env, verbose=1, seed=0)

    print("===학습 시작===")
    print("화면의 ep_rew_mean(평균 보상)이 오르면 학습이 진행중")
    print("(참고: 아무것도 없는 무작위성 플레이시 평균보상은 -9.8)")
#     ckpt = CheckpointCallback(
#         save_freq=500_000,
#         save_path=os.path.join(os.path.dirname(__file__), "checkpoints"),
#         name_prefix="rogue_ppo",
# )
#     model.learn(total_timesteps=100_000_000, callback=ckpt)

    model.learn(total_timesteps=TOTAL_TIMESTEPS)

    model.save(MODEL_PATH)
    print("===학습 끝. 모델 저장: "+ MODEL_PATH + ".zip ===")

if __name__ == "__main__":
    main()# 어차피 메인 루프밖에 없는데 굳이 이걸 만들어야 할까요?