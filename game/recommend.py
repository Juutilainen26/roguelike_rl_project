import os
import sys
sys.path.append(os.path.dirname(__file__))

import numpy as np
import torch
from stable_baselines3 import PPO
from rogue_env import RogueEnv
import map

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_ppo")
ARROW={0:"위", 1:"아래", 2:"왼쪽",3:"오른쪽"}
DELTA={0:(0,-1), 1:(0,1), 2:(-1,0), 3:(1,0)}

def action_probs(model, obs):
    """AI가 각 행동(상/하/좌/우)을 얼마나 선호하는지 확률로 뽑아온다."""
    obs_t=model.policy.obs_to_tensor(obs)[0]
    with torch.no_grad():
        dist=model.policy.get_distribution(obs_t)
        probs=dist.distribution.probs
    return probs.cpu().numpy()[0]

def reason(env, action):
    """추천 행동이 왜 좋은지, 그 방향 칸에 뭐가 있는지로 사람 말 설명을 만든다."""
    dx, dy=DELTA[action]
    tx, ty=env.px+dx, env.py+dy

    if env.game_map[ty][tx]==map.WALL:
        return "그쪽은 벽. (AI가 헷갈리는 낯선 상황일 수 있음)"
    if (tx, ty)==(map.WIDTH-2, map.HEIGHT-2):
        return "출구. 다음으로 진행"
    
    en=env._find_at(env.enemies, tx, ty)
    if en is not None:
        if en.get("boss"):
            if env.atk>=en["hp"]:
                return f"보스가 있다. 지금 공격력({env.atk})이면 원킬 가능. 공격!"
            return f"보스(체력{en['hp']}). 공격력({env.atk})이 애매하면 위험. 무기 강매"
        return "적 발견, 처치하면 점수 획득(퍼스트킬 보너스 있음)"
    
    it=env._find_at(env.items, tx, ty)
    if it is not None:
        if it["kind"]=="weapon":
            return "저기 무기. 먹고 공격력 업 실시"
        if env.hp<=6:
            return "체력 낮음. 저쪽 포션. 회복 필요"
        return "포션 발견, 체력 회복 가능"
    
    return "이 방향이 목표에 가까워 지는길이라고 AI가 판단했어요."

def main():
    model=PPO.load(MODEL_PATH)
    env=RogueEnv()
    obs, info = env.reset(seed=0)

    print("==== AI 코치와 함께 플레이 ====")
    print("매 턴 AI가 추천을 알려줍니다. 엔터=추천대로 / w, s, a, d=직접 이동 / q=종료\n")

    terminated=truncated=False
    reward=0.0
    while not (terminated or truncated):
        env.render()
        probs=action_probs(model, obs)
        best=int(np.argmax(probs))

        print(f"\n[AI 추천] {ARROW[best]}  (확신도 {probs[best]*100:.0f}%)")
        print(f"이유: {reason(env,best)}")
        allp=", ".join(f"{ARROW[a]} {probs[a]*100:.0f}%" for a in range(4))
        print(f"(전체 선호도: {allp})")

        key=input("플레이어의 선택 > ").strip()
        if key=="q":
            print("종료합니다.")
            return
        keymap={"w":0, "s":1, "a":2, "d":3, "":best}
        if key not in keymap:
            print("w, a, s, d, 엔터, q 중에서 입력하세요.")
            continue
        obs, reward, terminated, truncated, info=env.step(keymap[key])

    env.render()
    print("\n보스 처리! 클리어!" if terminated and reward > 0 else "\n게임 종료")

if __name__=="__main__":
    main()