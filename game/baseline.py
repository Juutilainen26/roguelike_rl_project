import numpy as np
from rogue_env import RogueEnv

EPISODES=300

env=RogueEnv()
env.action_space.seed(0)

rewards=[]
floors=[]
steps_list=[]
outcomes={"클리어":0, "사망":0, "시간초과":0}# 초기값 지정인듯?

for ep in range(EPISODES):
    obs, info=env.reset(seed=ep)# 시드 0으로 고정한다는게 아니라 매판이 1,2,3 똑같이 진행되게 한다는것
    total=0.0
    terminated=False
    truncated=False

    while not (terminated or truncated):
        action=env.action_space.sample()
        obs, reward, terminated, truncated, info=env.step(action)
        total+=reward

    rewards.append(total)
    floors.append(env.floor)
    steps_list.append(env.steps)

    if env.hp<=0:
        outcomes["사망"]+=1
    elif terminated:
        outcomes["클리어"]+=1
    else:
        outcomes["시간초과"]+=1

rewards=np.array(rewards)

print("="*45)
print(f"무작위 기준선 측정 (에피소드 {EPISODES}판)")
print("="*45)
print(f"평균 보상    : {rewards.mean():7.2f}")# 왜 7.2f가 붙지? :.2f면 소숫점 2자리까지인걸로 아는데
print(f"보상 범위    : 최소 {rewards.min():.1f} ~ 최대 {rewards.max():.1f}")
print(f"보상 표준편차 : {rewards.std():7.2f}   (클수록 편차가 크다.)")
print(f"평균 도달 층  : {np.mean(floors):7.2f}  (최대 {max(floors)}층)")
print(f"평균 걸음수   : {np.mean(steps_list):7.1f}")
print(f"="*45)
print(f"클리어  : {outcomes['클리어']:4d}판  ({outcomes['클리어']/EPISODES*100:5.1F}%)")
print(f"사망    : {outcomes['사망']:4d}판  ({outcomes['사망']/EPISODES*100:5.1f}%)")
print(f"시간초과 : {outcomes['시간초과']:4d}판  ({outcomes['시간초과']/EPISODES*100:5.1f}%)")
print("="*45)
print("이건 아무것도 모르는 상태의 AI다. 이후 얼마나 성장하는지 눈으로 보자")