# =============================================================================
# game/evaluate_cnn_claude.py  (CNN 모델 성적표 — MLP와 같은 방식으로 비교)
# 실행: python game/evaluate_cnn_claude.py
# =============================================================================
import os
import sys
sys.path.append(os.path.dirname(__file__))

import numpy as np
from stable_baselines3 import PPO
from rogue_env_cnn import RogueEnvCNN

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_cnn")
EPISODES = 300


def main():
    env = RogueEnvCNN()
    model = PPO.load(MODEL_PATH)
    rewards, floors, steps_list = [], [], []
    outcomes = {"클리어": 0, "사망": 0, "시간초과": 0}

    for ep in range(EPISODES):
        obs, info = env.reset(seed=ep)
        total = 0.0
        terminated = truncated = False
        while not (terminated or truncated):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            total += reward
        rewards.append(total); floors.append(env.floor); steps_list.append(env.steps)
        if env.hp <= 0: outcomes["사망"] += 1
        elif terminated: outcomes["클리어"] += 1
        else: outcomes["시간초과"] += 1

    rewards = np.array(rewards)
    print("=" * 46)
    print(f" CNN 성적표 (무작위 맵, {EPISODES}판)")
    print("=" * 46)
    print(f" 평균 보상   : {rewards.mean():7.2f}")
    print(f" 평균 도달 층 : {np.mean(floors):7.2f}")
    print(f" 클리어   : {outcomes['클리어']/EPISODES*100:5.1f}%")
    print(f" 사망     : {outcomes['사망']/EPISODES*100:5.1f}%")
    print(f" 시간초과 : {outcomes['시간초과']/EPISODES*100:5.1f}%")
    print("=" * 46)
    print(" (비교: 같은 무작위 맵에서 MLP는 클리어 1~2% 수준이었음)")


if __name__ == "__main__":
    main()
