import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np

import map

C_FLOOR, C_WALL, C_PLAYER, C_ENEMY, C_BOSS, C_WEAPON, C_POTION, C_EXIT = 0, 1, 2, 3, 4, 5, 6, 7

NUM_FLOORS = 2
ENEMY_DAMAGE = 2
BOSS_HP = 5
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

class RogueEnv(gym.Env):
    def __init__(self, encounter_chance=ENCOUNTER_CHANCE):
        super().__init__()
        self.encounter_chance=encounter_chance

        self.action_space = spaces.Discrete(4)

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
        # 맵 고정: 매 판 같은 위치에 배치(학습이 실제로 되도록 무작위성 제거)
        if floor == 1:
            enemies=[{"x":5,"y":2,"hp":3}, {"x":7,"y":4,"hp":3}]
            items=[{"x":3,"y":1,"kind":"weapon"}, {"x":2,"y":5,"kind":"potion"}]
        else:  # 보스층
            enemies=[{"x":4,"y":1,"hp":3}, {"x":6,"y":5,"hp":3},
                     {"x":8,"y":3,"hp":BOSS_HP,"boss":True}]
            items=[{"x":2,"y":1,"kind":"weapon"}, {"x":3,"y":5,"kind":"potion"}]
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

        return self._get_obs(), {}
        
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
                        reward +=R_FIRSTKILL
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
                if random.random() < self.encounter_chance:
                    if self.atk >= ENCOUNTER_HP:
                        reward += R_KILL
                        if not self.killed_this_floor:
                            reward += R_FIRSTKILL
                            self.killed_this_floor=True
                    else:
                        self.hp-=ENEMY_DAMAGE
                        reward +=R_HIT

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
    
    def render(self):
        grid=map.make_map(map.WIDTH, map.HEIGHT)
        map.place(grid, map.WIDTH-2, map.HEIGHT-2, map.EXIT)
        for it in self.items:
            map.place(grid, it["x"], it["y"], "/" if it["kind"]=="weapon" else "+")
        for en in self.enemies:
            map.place(grid, en["x"], en["y"], "B" if en.get("boss") else "g")
        map.place(grid, self.px, self.py, map.PLAYER)
        print(f"[{self.floor}층] HP:{self.hp} ATK:{self.atk} steps:{self.steps}")
        map.print_map(grid)