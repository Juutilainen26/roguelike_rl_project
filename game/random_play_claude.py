# =============================================================================
# game/random_play.py   (5주차 예제 — 무작위 에이전트로 환경 테스트)
# 목적: 아직 학습 안 한 AI가, 우리 게임을 '무작위 행동'으로 자동 플레이하게 해본다.
#       → 5주차 완료 기준: "AI가 무작위로라도 게임을 자동 플레이한다".
#
# 실행: 터미널에서   python game/random_play.py
# =============================================================================

from roguelike_rl_project.game.rogue_env_claude import RogueEnv   # 방금 만든 환경 가져오기

env = RogueEnv()

EPISODES = 5   # 몇 판 돌려볼지

for ep in range(1, EPISODES + 1):
    obs, info = env.reset(seed=ep)   # 판 초기화 (seed로 매판 고정된 무작위)
    total_reward = 0.0
    done = False

    while not done:
        action = env.action_space.sample()   # ★ 무작위로 행동 하나 뽑기 (아직 안 똑똑함)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        done = terminated or truncated       # 끝났거나(승리/사망) 끊겼으면(시간초과) 종료

    result = "클리어!" if terminated and reward > 0 else ("사망/시간초과")
    print(f"에피소드 {ep}: 총보상 {total_reward:.1f}, {result} (걸음수 {env.steps})")

print("\n무작위 플레이 끝. 환경이 정상 작동한다는 뜻입니다.")
print("아직 AI는 아무것도 안 배웠습니다. 학습은 7주차부터!")
