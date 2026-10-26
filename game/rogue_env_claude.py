# =============================================================================
# game/rogue_env_claude.py  (8주차 v2 — 보상 재설계 + 포켓몬식 랜덤 인카운터)
#  변경점 요약:
#   1) 보상 상수 재조정 (걸음벌점 완화, 층클리어 강화, 사망벌점 완화)
#   2) R_FIRSTKILL: 각 층에서 '첫 처치'에 보너스 (층마다 최소 1마리 유도)
#   3) ENCOUNTER: 빈 칸을 걸으면 확률적으로 '피할 수 없는 전투' 발생
#      - 공격력(atk) >= ENCOUNTER_HP 이면 승리(처치 보상), 아니면 피해
#      - 즉 무기를 챙겨야 인카운터가 위협에서 이득으로 바뀜
# =============================================================================
import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np

import map

C_FLOOR, C_WALL, C_PLAYER, C_ENEMY, C_BOSS, C_WEAPON, C_POTION, C_EXIT = 0, 1, 2, 3, 4, 5, 6, 7
# AI는 1로 같혀진 0바닥을 딛고 있는건가?

NUM_FLOORS = 3
ENEMY_DAMAGE = 2
BOSS_HP = 8
BOSS_DAMAGE = 3
MAX_STEPS = 200

R_STEP=-0.02
R_WALL=-0.1
R_KILL=1.0
R_FIRSTKILL=1.0
R_HIT=-0.3
R_ITEM=0.5
R_FLOOR=3.0
R_WIN=10.0
R_DEATH=-5.0
ENCOUNTER_CHANCE=0.15
ENCOUNTER_HP=3
# 아마 나중에는 각 아이템별 보상값도 바꾸겠지요?
# 만점과 낙제점은 따로 존재하지 않고 최대한 높은 점수를 위해 학습을 진행하는건가?

class RogueEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.action_space = spaces.Discrete(4)# 0~3까지를 방향지정은 어디서 해준거지?

        obs_len=map.WIDTH*map.HEIGHT+3
        self.observation_space = spaces.Box(low=0, high=255, shape=(obs_len,), dtype=np.float32)

    def _random_cell(self, occupied):
        while True:
            x=random.randint(1, map.WIDTH-2)
            y=random.randint(1, map.HEIGHT-2)
            if (x, y) not in occupied:
                occupied.add((x, y))
                return x, y
            
    def _make_floor(self, floor):
        occupied={(1, 1), (map.WIDTH-2, map.HEIGHT-2)}
        enemies, items=[], []
        for _ in range(2):
            x, y= self._random_cell(occupied)
            enemies.append({"x":x, "y":y, "hp":3})
        x, y = self._random_cell(occupied)
        items.append({"x":x, "y":y, "kind":"weapon"})
        x, y = self._random_cell(occupied)
        items.append({"x":x, "y":y, "kind":"potion"})
        if floor==NUM_FLOORS:
            x, y = self._random_cell(occupied)
            enemies.append({"x":x, "y":y, "hp":BOSS_HP, "boss":True})
        return enemies, items
    
    def _find_at(self, entities, x, y):
        for e in entities:
            if e["x"]==x and e["y"]==y:
                return e
        return None
    
    def _get_obs(self):
        grid=map.make_map(map.WIDTH, map.HEIGHT)
        code=[[C_WALL if cell == map.WALL else C_FLOOR for cell in row] for row in grid]
        # 와...if문이랑 for문이 어떻게 연결된건지 머리아프네요.
        code[map.HEIGHT-2][map.WIDTH-2]=C_EXIT
        for it in self.items:
            code[it["y"]][it["x"]] = C_WEAPON if it["kind"]=="weapon" else C_POTION
        for en in self.enemies:
            code[en["y"]][en["x"]] = C_BOSS if en.get("boss") else C_ENEMY
        code[self.py][self.px] = C_PLAYER

        flat=np.array(code, dtype=np.float32).flatten()
        extra=np.array([max(self.hp, 0), self.atk, self.floor], dtype=np.float32)
        return np.concatenate([flat, extra])
    
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            random.seed(seed)

        self.px, self.py=1,1
        self.hp=10
        self.atk=1
        self.floor=1
        self.killed_this_floor=False
        self.steps=0
        self.game_map=map.make_map(map.WIDTH, map.HEIGHT)
        self.enemies, self.items=self._make_floor(self.floor)

        return self._get_obs(), {}# 무슨 의미인지 전혀 모르겠다.
        
    def step(self, action):
        self.steps +=1
        reward=R_STEP
        terminated=False
        truncated=False

        nx, ny = self.px, self.py
        if action==0: ny-=1
        elif action==1: ny+=1
        elif action==2: nx-=1
        elif action==3: nx+=1

        if self.game_map[ny][nx]==map.WALL:
            reward +=R_WALL
            if self.steps>=MAX_STEPS:
                truncated=True
            return self._get_obs(), reward, terminated, truncated, {}
        
        target = self._find_at(self.enemies, nx, ny)
        if target is not None:
            target["hp"] -= self.atk
            if target["hp"] <= 0:
                self.enemies.remove(target)
                self.px, self.py = nx, ny
                if target.get("boss"):
                    reward += R_WIN
                    terminated=True
                else:
                    reward +=R_KILL
                    if not self.killed_this_floor:
                        reward += R_FIRSTKILL
                        self.killed_this_floor=True
            else:
                dmg=BOSS_DAMAGE if target.get("boss") else ENEMY_DAMAGE
                self.hp -=dmg
                reward +=R_HIT
        else:
            item = self._find_at(self.items, nx, ny)
            if item is not None:
                if item["kind"]=="potion":
                    self.hp +=5
                else:
                    self.atk+=2
                self.items.remove(item)
                reward +=R_ITEM
                self.px, self.py=nx, ny
            else:
                self.px, self.py=nx, ny
                if random.random() < ENCOUNTER_CHANCE:
                    if self.atk >= ENCOUNTER_HP:
                        reward += R_KILL
                        if not self.killed_this_floor:
                            reward += R_FIRSTKILL
                            self.killed_this_floor=True
                    else:
                        self.hp -= ENEMY_DAMAGE
                        reward += R_HIT

        if self.hp <=0:
            reward +=R_DEATH
            terminated=True
        
        if (not terminated) and self.px == map.WIDTH-2 and self.py == map.HEIGHT-2:
            if self.floor < NUM_FLOORS:
                self.floor +=1
                self.px, self.py=1, 1
                self.enemies, self.items=self._make_floor(self.floor)
                self.killed_this_floor=False
                reward += R_FLOOR

        if self.steps >= MAX_STEPS:
            truncated=True

        return self._get_obs(), reward, terminated, truncated, {}
    
    def render(self):#학습 할땐 없어도 되지만, 동시에 특정 학습 지점에서 그려주면 좋은 자료가 되겠지요?
        grid=map.make_map(map.WIDTH, map.HEIGHT)
        map.place(grid, map.WIDTH-2, map.HEIGHT-2, map.EXIT)
        for it in self.items:
            map.place(grid, it["x"], it["y"], "/" if it["kind"]=="weapon" else "+")
        for en in self.enemies:
            map.place(grid, en["x"], en["y"], "B" if en.get("boss") else "g")
        map.place(grid, self.px, self.py, map.PLAYER)
        print(f"[{self.floor}층] HP:{self.hp} ATK:{self.atk} steps:{self.steps}")
        map.print_map(grid)
