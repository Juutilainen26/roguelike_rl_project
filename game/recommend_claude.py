# =============================================================================
# game/recommend_claude.py  (전술 추천 — AI 코치와 함께 플레이)
#
# 학습된 AI를 '코치'로 쓴다. 매 턴 현재 상황에서 AI가 추천하는 행동과
# 확신도, 그리고 사람이 읽을 수 있는 이유를 알려준다.
# (설계 문서 7장: 상황을 주면 추천 행동과 이유를 알려준다)
#
# 실행: 프로젝트 폴더에서   python game/recommend_claude.py
#   각 턴: 엔터=AI 추천대로 이동 / w,a,s,d=직접 이동 / q=종료
# =============================================================================

import os
import sys
sys.path.append(os.path.dirname(__file__))

import numpy as np
import torch
from stable_baselines3 import PPO
from rogue_env import RogueEnv
import map

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_ppo")
ARROW = {0: "위", 1: "아래", 2: "왼쪽", 3: "오른쪽"}
DELTA = {0: (0, -1), 1: (0, 1), 2: (-1, 0), 3: (1, 0)}


def action_probs(model, obs):
    """AI가 각 행동(상/하/좌/우)을 얼마나 선호하는지 확률로 뽑아온다."""
    obs_t = model.policy.obs_to_tensor(obs)[0]
    with torch.no_grad():
        dist = model.policy.get_distribution(obs_t)
        probs = dist.distribution.probs
    return probs.cpu().numpy()[0]


def reason(env, action):
    """추천 행동이 왜 좋은지, 그 방향 칸에 뭐가 있는지로 사람 말 설명을 만든다."""
    dx, dy = DELTA[action]
    tx, ty = env.px + dx, env.py + dy

    if env.game_map[ty][tx] == map.WALL:
        return "그쪽은 벽이에요. (AI가 헷갈리는 낯선 상황일 수 있어요)"
    if (tx, ty) == (map.WIDTH - 2, map.HEIGHT - 2):
        return "출구 방향이에요. 다음 층으로 내려가거나 진행하는 길이에요."

    en = env._find_at(env.enemies, tx, ty)
    if en is not None:
        if en.get("boss"):
            if env.atk >= en["hp"]:
                return f"보스가 그쪽에 있어요! 지금 공격력({env.atk})이면 한 번에 잡을 수 있어요. 공격!"
            return f"보스예요(체력 {en['hp']}). 공격력({env.atk})이 부족하면 위험해요. 무기를 더 챙기는 게 좋아요."
        return "적이 있어요. 처치하면 점수를 얻고 첫 처치 보너스도 받아요."

    it = env._find_at(env.items, tx, ty)
    if it is not None:
        if it["kind"] == "weapon":
            return "그쪽에 무기가 있어요. 먼저 챙겨서 공격력을 올리세요."
        if env.hp <= 6:
            return "체력이 낮은데 그쪽에 포션이 있어요. 마셔서 회복하세요."
        return "그쪽에 포션이 있어요. 체력을 채워둘 수 있어요."

    return "이 방향이 목표(무기·보스·출구)로 가는 길이라고 AI가 판단했어요."


def main():
    model = PPO.load(MODEL_PATH)
    env = RogueEnv()
    obs, info = env.reset(seed=0)

    print("===== AI 코치와 함께 플레이 =====")
    print("매 턴 AI가 추천을 알려줍니다.  엔터=추천대로 / w,a,s,d=직접 이동 / q=종료\n")

    terminated = truncated = False
    reward = 0.0
    while not (terminated or truncated):
        env.render()
        probs = action_probs(model, obs)
        best = int(np.argmax(probs))

        print(f"\n[AI 추천] {ARROW[best]}  (확신도 {probs[best] * 100:.0f}%)")
        print(f"  이유: {reason(env, best)}")
        allp = ", ".join(f"{ARROW[a]} {probs[a] * 100:.0f}%" for a in range(4))
        print(f"  (전체 선호도: {allp})")

        key = input("당신의 선택 > ").strip()
        if key == "q":
            print("종료합니다.")
            return
        keymap = {"w": 0, "s": 1, "a": 2, "d": 3, "": best}
        if key not in keymap:
            print("w, a, s, d, 엔터, q 중에서 입력하세요.")
            continue
        obs, reward, terminated, truncated, info = env.step(keymap[key])

    env.render()
    print("\n보스 처치! 클리어! 🎉" if terminated and reward > 0 else "\n게임 종료")


if __name__ == "__main__":
    main()
