# =============================================================================
# game/evaluate_claude.py   (7주차 예제 — 학습된 AI 성적표 + 기준선 비교)
#
# train_claude.py 로 학습을 끝낸 뒤 실행한다.
# 학습된 AI를 무작위 기준선과 '같은 방식(300판)'으로 재서, 얼마나 좋아졌는지 본다.
#
# 실행: 프로젝트 폴더에서   python game/evaluate_claude.py
# =============================================================================

import os
import sys
sys.path.append(os.path.dirname(__file__))

import numpy as np
from stable_baselines3 import PPO
from rogue_env import RogueEnv

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_ppo")
EPISODES = 300

# --- 무작위 기준선 (6주차에 측정해 둔 값) : 비교 대상 ---
BASE_REWARD = -9.80
BASE_CLEAR = 1.0      # %
BASE_FLOOR = 1.66

def main():
    env = RogueEnv()
    model = PPO.load(MODEL_PATH)   # 학습된 뇌 불러오기

    rewards, floors, steps_list = [], [], []
    outcomes = {"클리어": 0, "사망": 0, "시간초과": 0}

    for ep in range(EPISODES):
        obs, info = env.reset(seed=ep)
        total = 0.0
        terminated = truncated = False
        while not (terminated or truncated):
            # deterministic=True : 무작위가 아니라 '학습으로 배운 최선의 행동'을 고른다.
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            total += reward
        rewards.append(total)
        floors.append(env.floor)
        steps_list.append(env.steps)
        if env.hp <= 0:
            outcomes["사망"] += 1
        elif terminated:
            outcomes["클리어"] += 1
        else:
            outcomes["시간초과"] += 1

    rewards = np.array(rewards)
    clear_pct = outcomes["클리어"] / EPISODES * 100

    print("=" * 50)
    print(f" 학습된 AI 성적표  (에피소드 {EPISODES}판)")
    print("=" * 50)
    print(f" 평균 보상   : {rewards.mean():7.2f}   (기준선 {BASE_REWARD})")
    print(f" 평균 도달 층 : {np.mean(floors):7.2f}   (기준선 {BASE_FLOOR})")
    print(f" 평균 걸음수  : {np.mean(steps_list):7.1f}")
    print("-" * 50)
    print(f" 클리어   : {outcomes['클리어']:4d}판 ({clear_pct:5.1f}%)   (기준선 {BASE_CLEAR}%)")
    print(f" 사망     : {outcomes['사망']:4d}판 ({outcomes['사망']/EPISODES*100:5.1f}%)")
    print(f" 시간초과 : {outcomes['시간초과']:4d}판 ({outcomes['시간초과']/EPISODES*100:5.1f}%)")
    print("=" * 50)
    # 간단한 판정
    if rewards.mean() > BASE_REWARD + 1:
        print(" → 기준선보다 평균 보상이 올랐습니다. 뭔가 '배웠다'는 신호! ")
    else:
        print(" → 기준선과 큰 차이 없음. 더 오래 학습하거나 보상 재설계가 필요할 수 있음.")

if __name__ == "__main__":
    main()
