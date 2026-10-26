# =============================================================================
# game/watch_claude.py  (학습된 AI의 플레이를 눈으로 관전하기)
#
# 100% 클리어하는 AI가 실제로 어떻게 움직이는지 한 걸음씩 보여준다.
# (스피드런 경로를 눈으로 확인 → 전술 추천의 재료)
#
# 실행: 프로젝트 폴더에서   python game/watch_claude.py
# =============================================================================

import os
import sys
import time
sys.path.append(os.path.dirname(__file__))

from stable_baselines3 import PPO
from rogue_env import RogueEnv

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_ppo")
ARROW = {0: "위", 1: "아래", 2: "왼쪽", 3: "오른쪽"}

def main():
    model = PPO.load(MODEL_PATH)
    env = RogueEnv()
    obs, info = env.reset(seed=0)

    print("===== 학습된 AI 관전 시작 =====")
    env.render()
    terminated = truncated = False
    total = 0.0

    while not (terminated or truncated):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(int(action))
        total += reward
        time.sleep(0.4)                      # 눈으로 볼 수 있게 잠깐 멈춤
        print(f"--- 행동: {ARROW[int(action)]}  (보상 {reward:+.2f}) ---")
        env.render()

    print(f"\n결과: {'보스 처치! 클리어!' if terminated and reward > 0 else '종료'}  총보상 {total:.1f}, {env.steps}걸음")

if __name__ == "__main__":
    main()
