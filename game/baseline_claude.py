# =============================================================================
# game/baseline_claude.py   (6주차 예제 — '무작위 기준선' 측정 도구)
#
# 왜 만드나?
#   학습을 시작하기 전에, "아무것도 안 배운 무작위 AI"가 우리 게임에서
#   평균 몇 점을 받고, 몇 층까지 가고, 보스를 몇 번 잡는지를 '숫자'로 재둔다.
#   나중에(7주차) 학습한 AI의 성적을 이 숫자와 비교해서 "배웠다"를 증명한다.
#   → 즉, 이건 '시험 전에 재두는 기초 체력 측정'이다.
#
# 실행: 터미널에서   python game/baseline_claude.py
# =============================================================================

import numpy as np
from roguelike_rl_project.game.rogue_env import RogueEnv       # 사용자가 만든 환경 (game/env.py)

EPISODES = 300                 # 많이 돌릴수록 평균이 안정적 (무작위라 편차가 큼)

env = RogueEnv()
env.action_space.seed(0)       # 행동 뽑기도 재현 가능하게 고정 (매번 같은 결과)

rewards = []                   # 판마다 총보상
floors = []                    # 판마다 도달한 최고 층
steps_list = []                # 판마다 걸음수
outcomes = {"클리어": 0, "사망": 0, "시간초과": 0}   # 결과 종류별 횟수

for ep in range(EPISODES):
    obs, info = env.reset(seed=ep)     # seed로 매 판 맵을 고정(재현 가능)
    total = 0.0
    terminated = False
    truncated = False

    while not (terminated or truncated):
        action = env.action_space.sample()             # 무작위 행동
        obs, reward, terminated, truncated, info = env.step(action)
        total += reward

    # 한 판이 끝났다. 결과를 기록한다.
    rewards.append(total)
    floors.append(env.floor)
    steps_list.append(env.steps)

    # 어떻게 끝났는지 분류: 체력 0이면 사망 / terminated면 보스처치(클리어) / 나머지는 시간초과
    if env.hp <= 0:
        outcomes["사망"] += 1
    elif terminated:
        outcomes["클리어"] += 1
    else:
        outcomes["시간초과"] += 1

# ------- 통계 계산 및 출력 -------
rewards = np.array(rewards)

print("=" * 45)
print(f" 무작위 기준선 측정  (에피소드 {EPISODES}판)")
print("=" * 45)
print(f" 평균 보상   : {rewards.mean():7.2f}")
print(f" 보상 범위   : 최소 {rewards.min():.1f}  ~  최대 {rewards.max():.1f}")
print(f" 보상 표준편차: {rewards.std():7.2f}   (클수록 들쭉날쭉)")
print(f" 평균 도달 층 : {np.mean(floors):7.2f}   (최대 {max(floors)}층)")
print(f" 평균 걸음수  : {np.mean(steps_list):7.1f}")
print("-" * 45)
print(f" 클리어   : {outcomes['클리어']:4d}판  ({outcomes['클리어']/EPISODES*100:5.1f}%)")
print(f" 사망     : {outcomes['사망']:4d}판  ({outcomes['사망']/EPISODES*100:5.1f}%)")
print(f" 시간초과 : {outcomes['시간초과']:4d}판  ({outcomes['시간초과']/EPISODES*100:5.1f}%)")
print("=" * 45)
print(" 이 숫자들을 기억해 두자. 학습 후(7주차) 이보다")
print(" 얼마나 좋아지는지가 '학습됐다'의 증거가 된다.")
