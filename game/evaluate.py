import os
import sys
sys.path.append(os.path.dirname(__file__))

import numpy as np
from stable_baselines3 import PPO
from rogue_env import RogueEnv

MODEL_PATH=os.path.join(os.path.dirname(__file__), "rogue_PPO")
EPISODES=300

BASE_REWARD=1.95
BASE_CLEAR=0.7
BASE_FLOOR=1.28

def main():
    env=RogueEnv()
    model=PPO.load(MODEL_PATH)

    rewards, floors, steps_list=[], [], []
    outcomes={"클리어":0, "사망":0, "시간초과":0}

    for ep in range(EPISODES):
        obs, info=env.reset(seed=ep)
        total=0.0
        terminated=truncated=False
        while not (terminated or truncated):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            total+=reward
        rewards.append(total)
        floors.append(env.floor)
        steps_list.append(env.steps)
        if env.hp <=0:
            outcomes["사망"]+=1
        elif terminated:
            outcomes["클리어"]+=1
        else:
            outcomes["시간초과"]+=1

    rewards=np.array(rewards)
    clear_pct=outcomes["클리어"]/EPISODES*100

    print("=" * 50)
    print(f" 학습된 AI 성적표  (에피소드 {EPISODES}판)")
    print("=" * 50)
    print(f" 평균 보상   : {rewards.mean():7.2f}   (기준선 {BASE_REWARD})")# 여전히 모르겠다. :.2f는 소숫점 둘째자리까지라는건데 7은 뭐지?
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
    main()#여기도 def함수 하나밖에 없는데 굳이 이걸로 실행하게 해야 할까?