# =============================================================================
# game/play_gui_claude.py  (파이게임 그래픽 버전 — 사람 플레이 + AI 관전)
#
#   그림은 "사람이 볼 때만" 쓰는 창이다. 학습은 지금처럼 구조 입력(격자)으로
#   빠르게 하고, 이건 순수하게 보고 즐기는 용도.
#   게임 규칙은 rogue_env(RogueEnv)를 그대로 재사용한다.
#
# 설치: pip install pygame
# 실행:
#   사람 플레이:  python game/play_gui_claude.py
#   AI 관전   :  python game/play_gui_claude.py ai
#     (AI 관전은 학습된 rogue_ppo.zip 이 필요)
# 조작: 방향키 또는 w/a/s/d 이동,  R 다시하기,  ESC/창닫기 종료
# =============================================================================

import os
import sys
sys.path.append(os.path.dirname(__file__))

import pygame
from rogue_env import RogueEnv
import map

MODE = "ai" if (len(sys.argv) > 1 and sys.argv[1] == "ai") else "human"
CELL = 48
BAR = 44                     # 아래 상태바 높이
AI_STEP_MS = 300             # AI 관전 시 한 걸음 간격(ms)

# 색상
COL_BG    = (25, 25, 30)
COL_FLOOR = (210, 210, 215)
COL_WALL  = (45, 45, 55)
COL_LINE  = (180, 180, 185)
COL_TEXT  = (240, 240, 240)
ENT = {   # (색, 글자)
    "player": ((70, 130, 230), "@"),
    "enemy":  ((210, 70, 70),  "g"),
    "boss":   ((160, 60, 190), "B"),
    "weapon": ((225, 185, 55), "/"),
    "potion": ((70, 185, 100), "+"),
    "exit":   ((235, 215, 110), "E"),
}


def cell_rect(x, y):
    return pygame.Rect(x * CELL, y * CELL, CELL, CELL)


def draw_entity(screen, font, x, y, kind):
    color, letter = ENT[kind]
    rect = cell_rect(x, y).inflate(-8, -8)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    t = font.render(letter, True, (20, 20, 20))
    screen.blit(t, t.get_rect(center=cell_rect(x, y).center))


def draw(screen, env, font, small, message=None):
    screen.fill(COL_BG)
    # 바닥/벽
    for y in range(map.HEIGHT):
        for x in range(map.WIDTH):
            is_wall = env.game_map[y][x] == map.WALL
            pygame.draw.rect(screen, COL_WALL if is_wall else COL_FLOOR, cell_rect(x, y))
            if not is_wall:
                pygame.draw.rect(screen, COL_LINE, cell_rect(x, y), 1)
    # 출구 → 아이템 → 적 → 플레이어 (나중에 그린 게 위)
    draw_entity(screen, font, map.WIDTH - 2, map.HEIGHT - 2, "exit")
    for it in env.items:
        draw_entity(screen, font, it["x"], it["y"], "weapon" if it["kind"] == "weapon" else "potion")
    for en in env.enemies:
        draw_entity(screen, font, en["x"], en["y"], "boss" if en.get("boss") else "enemy")
    draw_entity(screen, font, env.px, env.py, "player")
    # 상태바
    bar_y = map.HEIGHT * CELL
    pygame.draw.rect(screen, (15, 15, 20), (0, bar_y, map.WIDTH * CELL, BAR))
    who = "AI 관전" if MODE == "ai" else "직접 플레이"
    info = f"HP {env.hp}   ATK {env.atk}   Floor {env.floor}/2   [{who}]"
    screen.blit(small.render(info, True, COL_TEXT), (12, bar_y + 12))
    # 종료 메시지
    if message:
        overlay = pygame.Surface((map.WIDTH * CELL, map.HEIGHT * CELL), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        big = font.render(message, True, (255, 240, 120))
        screen.blit(big, big.get_rect(center=(map.WIDTH * CELL // 2, map.HEIGHT * CELL // 2)))
        sub = small.render("R: 다시하기    ESC: 종료", True, COL_TEXT)
        screen.blit(sub, sub.get_rect(center=(map.WIDTH * CELL // 2, map.HEIGHT * CELL // 2 + 40)))


def main():
    pygame.init()
    W, H = map.WIDTH * CELL, map.HEIGHT * CELL + BAR
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("로그라이크 강화학습")
    # 한글 폰트(윈도우: 맑은 고딕). 없으면 기본 폰트로.
    try:
        font = pygame.font.SysFont("malgungothic", 30, bold=True)
        small = pygame.font.SysFont("malgungothic", 22)
    except Exception:
        font = pygame.font.Font(None, 34); small = pygame.font.Font(None, 26)
    clock = pygame.time.Clock()

    model = None
    if MODE == "ai":
        from stable_baselines3 import PPO
        model = PPO.load(os.path.join(os.path.dirname(__file__), "rogue_ppo"))

    env = RogueEnv()
    obs, info = env.reset(seed=0)
    terminated = truncated = False
    reward = 0.0
    last_ai = 0

    running = True
    while running:
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    obs, info = env.reset(seed=0); terminated = truncated = False
                elif MODE == "human" and not (terminated or truncated):
                    if event.key in (pygame.K_UP, pygame.K_w): action = 0
                    elif event.key in (pygame.K_DOWN, pygame.K_s): action = 1
                    elif event.key in (pygame.K_LEFT, pygame.K_a): action = 2
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): action = 3

        # AI 관전: 일정 간격마다 한 걸음
        if MODE == "ai" and not (terminated or truncated):
            now = pygame.time.get_ticks()
            if now - last_ai >= AI_STEP_MS:
                act, _ = model.predict(obs, deterministic=True)
                action = int(act); last_ai = now

        if action is not None and not (terminated or truncated):
            obs, reward, terminated, truncated, info = env.step(action)

        msg = None
        if terminated or truncated:
            msg = "보스 처치! 클리어!" if (terminated and reward > 0) else "게임 종료"
        draw(screen, env, font, small, msg)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
