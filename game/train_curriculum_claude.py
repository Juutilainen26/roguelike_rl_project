# =============================================================================
# game/train_curriculum_claude.py   (8주차 v3 — 커리큘럼 학습)
#
# 아이디어: "걷기부터 배우고 뛰게 한다".
#   처음부터 위험한 필드에 던지면 AI가 겁먹고 벽에 숨는다(v2에서 확인).
#   그래서 위험 없는 안전한 세상부터 기본기를 익히게 하고,
#   같은 두뇌를 유지한 채 난이도(인카운터 확률)를 단계적으로 올린다.
#
#   ※ 먼저 rogue_env.py 를 encounter_chance 파라미터를 받도록 고쳐야 합니다.
#     (아래 대화에서 안내한 2줄 수정)
#
# 실행: 프로젝트 폴더에서   python game/train_curriculum_claude.py
# =============================================================================

import os
import sys
sys.path.append(os.path.dirname(__file__))

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from rogue_env import RogueEnv
from stable_baselines3.common.callbacks import CheckpointCallback

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_ppo")

# (인카운터 확률, 학습 걸음수) — 안전한 세상(0.0)부터 전체 난이도(0.15)까지
STAGES = [
    (0.0,  15_000_000),   # 1단계: 위험 없음 → 길 찾기/전투/층 넘기 기본기
    (0.06, 15_000_000),   # 2단계: 약한 위험 → 인카운터에 적응
    (0.12, 20_000_000),   # 3단계: 전체 난이도
]


def main():
    model = None
    for i, (chance, steps) in enumerate(STAGES, start=1):
        env = Monitor(RogueEnv(encounter_chance=chance))
        if model is None:
            model = PPO("MlpPolicy", env, verbose=1, seed=0)
        else:
            model.set_env(env)   # 배운 두뇌는 그대로, 환경 난이도만 교체
        print("")
        print("===== 커리큘럼 " + str(i) + "단계: 인카운터 확률 " + str(chance) + ", " + str(steps) + "걸음 =====")
        print("(안전한 1단계에서 ep_rew_mean 이 깔끔하게 오르는지 먼저 보세요.)")
        ckpt = CheckpointCallback(
            save_freq=1_000_000,
            save_path=os.path.join(os.path.dirname(__file__), "checkpoints"),
            name_prefix=f"stage{i}",
        )
        model.learn(total_timesteps=steps, callback=ckpt)
        #model.learn(total_timesteps=steps)
    model.save(MODEL_PATH + f"_stage{i}")
    #model.save(MODEL_PATH)
    print("")
    print("=== 커리큘럼 학습 끝. evaluate.py 로 전체 난이도 성적을 확인하세요. ===")


if __name__ == "__main__":
    main()
