# =============================================================================
# play/play_compare_gui.py  (파이게임 — 사람 플레이 + MLP vs CNN 추천 동시 비교)
#   같은 상황을 두 두뇌(MLP=납작 관측, CNN=이미지 관측)가 어떻게 판단하는지 나란히.
# 설치: pip install pygame     실행: python play/play_compare_gui.py
# 조작: 방향키/wasd 이동, R 다시하기, ESC 종료
# =============================================================================
import os, sys
sys.path.append(os.path.dirname(__file__))
import numpy as np
import pygame
import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import map
import rogue_env as RE
from rogue_env import RogueEnv


class SmallCNN(BaseFeaturesExtractor):          # CNN 모델 로드에 필요한 정의
    def __init__(self, observation_space, features_dim=128):
        super().__init__(observation_space, features_dim)
        n_ch = observation_space.shape[0]
        self.cnn = nn.Sequential(
            nn.Conv2d(n_ch, 16, 3, 1, 1), nn.ReLU(),
            nn.Conv2d(16, 32, 3, 1, 1), nn.ReLU(), nn.Flatten())
        with torch.no_grad():
            n_flat = self.cnn(torch.as_tensor(observation_space.sample()[None]).float()).shape[1]
        self.linear = nn.Sequential(nn.Linear(n_flat, features_dim), nn.ReLU())
    def forward(self, x):
        return self.linear(self.cnn(x))


CELL = 44; PANEL_W = 360; BAR = 40
ARROW = {0: "위", 1: "아래", 2: "왼쪽", 3: "오른쪽"}
DELTA = {0: (0,-1), 1: (0,1), 2: (-1,0), 3: (1,0)}
COL_BG=(25,25,30); COL_FLOOR=(210,210,215); COL_WALL=(45,45,55); COL_LINE=(180,180,185); COL_TEXT=(235,235,240)
ENT={"player":((70,130,230),"@"),"enemy":((210,70,70),"g"),"boss":((160,60,190),"B"),
     "weapon":((225,185,55),"/"),"potion":((70,185,100),"+"),"exit":((235,215,110),"E")}


def image_obs(env):
    grid = map.make_map(map.WIDTH, map.HEIGHT)
    code = [[RE.C_WALL if c == map.WALL else RE.C_FLOOR for c in row] for row in grid]
    code[map.HEIGHT-2][map.WIDTH-2] = RE.C_EXIT
    for it in env.items:
        code[it["y"]][it["x"]] = RE.C_WEAPON if it["kind"]=="weapon" else RE.C_POTION
    for en in env.enemies:
        code[en["y"]][en["x"]] = RE.C_BOSS if en.get("boss") else RE.C_ENEMY
    code[env.py][env.px] = RE.C_PLAYER
    g = np.array(code, dtype=np.float32)/7.0
    hp = np.full((map.HEIGHT, map.WIDTH), min(env.hp,20)/20.0, dtype=np.float32)
    at = np.full((map.HEIGHT, map.WIDTH), min(env.atk,20)/20.0, dtype=np.float32)
    fl = np.full((map.HEIGHT, map.WIDTH), env.floor/RE.NUM_FLOORS, dtype=np.float32)
    return np.stack([g, hp, at, fl], axis=0)


def probs_of(model, obs):
    obs_t = model.policy.obs_to_tensor(obs)[0]
    with torch.no_grad():
        p = model.policy.get_distribution(obs_t).distribution.probs
    return p.cpu().numpy()[0]


def reason(env, a):
    dx, dy = DELTA[a]; tx, ty = env.px+dx, env.py+dy
    if env.game_map[ty][tx] == map.WALL: return "벽 방향"
    if (tx, ty) == (map.WIDTH-2, map.HEIGHT-2): return "출구 방향"
    en = env._find_at(env.enemies, tx, ty)
    if en is not None: return "보스와 전투!" if en.get("boss") else "적과 전투"
    it = env._find_at(env.items, tx, ty)
    if it is not None: return "무기 획득" if it["kind"]=="weapon" else "포션 획득"
    return "목표로 이동"


def get_rec(model, obs, env):
    if model is None: return None
    p = probs_of(model, obs); best = int(np.argmax(p))
    return {"probs": p, "best": best, "reason": reason(env, best)}


def cell_rect(x, y): return pygame.Rect(x*CELL, y*CELL, CELL, CELL)


def draw_entity(screen, font, x, y, kind):
    color, letter = ENT[kind]
    pygame.draw.rect(screen, color, cell_rect(x, y).inflate(-8, -8), border_radius=8)
    t = font.render(letter, True, (20,20,20)); screen.blit(t, t.get_rect(center=cell_rect(x, y).center))


def panel(screen, x0, y0, h, title, rec, font, small, tcol):
    pygame.draw.rect(screen, (18,18,24), (x0, y0, PANEL_W, h))
    pygame.draw.line(screen, (60,60,70), (x0, y0), (x0+PANEL_W, y0), 1)
    screen.blit(font.render(title, True, tcol), (x0+16, y0+10))
    if rec is None:
        screen.blit(small.render("모델 없음 (rogue_cnn.zip 필요)", True, COL_TEXT), (x0+16, y0+48)); return
    screen.blit(font.render("→ " + ARROW[rec["best"]], True, (255,240,120)), (x0+16, y0+44))
    screen.blit(small.render(f"확신도 {rec['probs'][rec['best']]*100:.0f}%   ({rec['reason']})", True, (200,220,255)), (x0+16, y0+80))
    dist = "   ".join(f"{ARROW[a]} {rec['probs'][a]*100:.0f}%" for a in range(4))
    screen.blit(small.render(dist, True, COL_TEXT), (x0+16, y0+108))


def draw(screen, env, font, small, rec_mlp, rec_cnn, message):
    screen.fill(COL_BG)
    for y in range(map.HEIGHT):
        for x in range(map.WIDTH):
            wall = env.game_map[y][x]==map.WALL
            pygame.draw.rect(screen, COL_WALL if wall else COL_FLOOR, cell_rect(x, y))
            if not wall: pygame.draw.rect(screen, COL_LINE, cell_rect(x, y), 1)
    draw_entity(screen, font, map.WIDTH-2, map.HEIGHT-2, "exit")
    for it in env.items: draw_entity(screen, font, it["x"], it["y"], "weapon" if it["kind"]=="weapon" else "potion")
    for en in env.enemies: draw_entity(screen, font, en["x"], en["y"], "boss" if en.get("boss") else "enemy")
    draw_entity(screen, font, env.px, env.py, "player")
    by = map.HEIGHT*CELL
    pygame.draw.rect(screen, (15,15,20), (0, by, map.WIDTH*CELL, BAR))
    screen.blit(small.render(f"HP {env.hp}   ATK {env.atk}   Floor {env.floor}/{RE.NUM_FLOORS}   (방향키 이동)", True, COL_TEXT), (12, by+11))
    px = map.WIDTH*CELL; ph = map.HEIGHT*CELL; half = ph//2
    panel(screen, px, 0, half, "MLP 추천", rec_mlp, font, small, (120,200,255))
    panel(screen, px, half, ph-half, "CNN 추천", rec_cnn, font, small, (255,180,120))
    if message:
        ov = pygame.Surface((map.WIDTH*CELL, ph), pygame.SRCALPHA); ov.fill((0,0,0,150)); screen.blit(ov,(0,0))
        screen.blit(font.render(message, True, (255,240,120)), font.render(message,True,(0,0,0)).get_rect(center=(map.WIDTH*CELL//2, ph//2)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((map.WIDTH*CELL + PANEL_W, map.HEIGHT*CELL + BAR))
    pygame.display.set_caption("MLP vs CNN 추천 비교")
    try:
        font = pygame.font.SysFont("malgungothic", 26, bold=True); small = pygame.font.SysFont("malgungothic", 19)
    except Exception:
        font = pygame.font.Font(None, 28); small = pygame.font.Font(None, 22)

    here = os.path.dirname(__file__)
    def load(name):
        try: return PPO.load(os.path.join(here, name))
        except Exception as e: print(f"[{name}] 로드 실패: {e}"); return None
    model_mlp = load("rogue_ppo"); model_cnn = load("rogue_cnn")

    env = RogueEnv(); obs, info = env.reset(seed=0)
    terminated = truncated = False; reward = 0.0
    clock = pygame.time.Clock(); running = True
    while running:
        action = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: running = False
                elif e.key == pygame.K_r: obs, info = env.reset(); terminated = truncated = False
                elif not (terminated or truncated):
                    if e.key in (pygame.K_UP, pygame.K_w): action = 0
                    elif e.key in (pygame.K_DOWN, pygame.K_s): action = 1
                    elif e.key in (pygame.K_LEFT, pygame.K_a): action = 2
                    elif e.key in (pygame.K_RIGHT, pygame.K_d): action = 3
        rec_mlp = get_rec(model_mlp, obs, env)
        rec_cnn = get_rec(model_cnn, image_obs(env), env)
        if action is not None and not (terminated or truncated):
            obs, reward, terminated, truncated, info = env.step(action)
        msg = None
        if terminated or truncated:
            msg = "보스 처치! 클리어!" if (terminated and reward > 0) else "게임 종료 (R: 다시)"
        draw(screen, env, font, small, rec_mlp, rec_cnn, msg)
        pygame.display.flip(); clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
