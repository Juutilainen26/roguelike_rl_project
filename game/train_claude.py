# =============================================================================
# game/train_claude.py   (7주차 예제 — PPO로 실제 학습시키기)
#
# 드디어 AI를 '학습'시킨다. 지금까지는 무작위였지만, 이제 PPO 알고리즘이
# 보상을 높이는 방향으로 스스로 행동을 다듬어 간다.
#
# 실행: 프로젝트 폴더에서   python game/train_claude.py
#   (학습에는 CPU로 몇 분 걸립니다. 화면에 뜨는 ep_rew_mean 이 '평균 보상'인데,
#    이 값이 시간이 지나며 오르면 = AI가 배우고 있다는 뜻입니다.)
# =============================================================================

import os
import sys

# 어디서 실행하든 game 폴더 안의 rogue_env.py / map.py 를 찾도록 경로 추가
sys.path.append(os.path.dirname(__file__))

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from rogue_env import RogueEnv

TOTAL_TIMESTEPS = 300_000
MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_ppo")


def main():
    # Monitor로 감싸면 에피소드별 보상/길이가 자동 기록되어 ep_rew_mean 이 화면에 뜬다.
    env = Monitor(RogueEnv())

    # "MlpPolicy" = 관측(숫자 배열)을 받아 행동을 고르는 기본 신경망 두뇌.
    model = PPO("MlpPolicy", env, verbose=1, seed=0)

    print("=== 학습 시작 ===")
    print("화면의 ep_rew_mean(평균 보상)이 오르는지 지켜보세요. 오르면 배우는 중입니다.")
    print("(참고: 무작위 기준선의 평균 보상은 약 -9.8 이었습니다.)")

    model.learn(total_timesteps=TOTAL_TIMESTEPS)

    model.save(MODEL_PATH)
    print("=== 학습 끝. 모델 저장: " + MODEL_PATH + ".zip ===")
    print("이제 evaluate_claude.py 로 이 AI의 실력을 기준선과 비교해 보세요.")


if __name__ == "__main__":
    main()
