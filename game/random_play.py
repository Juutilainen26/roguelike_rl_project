from roguelike_rl_project.game.rogue_env import RogueEnv

env=RogueEnv()

EPISODES=5

for ep in range(1, EPISODES +1):# 1~5 6은 포함하지 않는다.
    obs, info = env.reset(seed=ep)
    total_reward=0.0
    done=False

    while not done:
        action=env.action_space.sample()
        obs, reward, terminated, truncated, info=env.step(action)
        total_reward+=reward
        done=terminated or truncated

    result="클리어!" if terminated and reward > 0 else("사망/시간초과")
    print(f"에피소드 {ep}: 총보상 {total_reward:.1f}, {result} (걸음수 {env.steps})")

print("\n무작위 플레이 끝. 노가다 잘 하다 갔음.")
print("아직 AI는 아무것도 안 배웠습니다. 멍청멍청")