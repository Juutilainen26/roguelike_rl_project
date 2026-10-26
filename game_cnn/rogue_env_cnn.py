# =============================================================================
# game/rogue_env_cnn.py  (CNN 비교군용 환경)
#   - 관측을 (채널, 세로, 가로) '이미지'로 준다 → CNN이 볼 수 있게.
#   - 맵은 '무작위'로 둔다(매번 다른 지도 = 일반화가 필요한 어려운 과제 = CNN이 빛날 무대).
#   - 나머지 규칙(전투/아이템/층/보스/보상)은 rogue_env를 그대로 상속.
# =============================================================================
import numpy as np
import gymnasium as gym
from gymnasium import spaces

import map
import rogue_env as base
from rogue_env import RogueEnv, NUM_FLOORS, BOSS_HP


class RogueEnvCNN(RogueEnv):
    def __init__(self, encounter_chance=base.ENCOUNTER_CHANCE):
        super().__init__(encounter_chance)
        # 관측: 4채널 이미지 [지도, 체력, 공격력, 층]  (값은 0~1로 정규화)
        C = 4
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(C, map.HEIGHT, map.WIDTH), dtype=np.float32)

    # 무작위 맵으로 되돌림 (부모의 고정 맵 대신)
    def _make_floor(self, floor):
        occupied={(1,1),(map.WIDTH-2,map.HEIGHT-2)}
        enemies,items=[],[]
        for _ in range(5):                       # 몬스터 맵당 5마리(눈에 보임)
            x,y=self._random_cell(occupied); enemies.append({"x":x,"y":y,"hp":3})
        x,y=self._random_cell(occupied); items.append({"x":x,"y":y,"kind":"weapon"})
        x,y=self._random_cell(occupied); items.append({"x":x,"y":y,"kind":"potion"})
        if floor==NUM_FLOORS:
            x,y=self._random_cell(occupied); enemies.append({"x":x,"y":y,"hp":BOSS_HP,"boss":True})
        return enemies,items

    # 관측을 이미지로 만든다
    def _get_obs(self):
        grid = map.make_map(map.WIDTH, map.HEIGHT)
        code = [[base.C_WALL if cell == map.WALL else base.C_FLOOR for cell in row] for row in grid]
        code[map.HEIGHT - 2][map.WIDTH - 2] = base.C_EXIT
        for it in self.items:
            code[it["y"]][it["x"]] = base.C_WEAPON if it["kind"] == "weapon" else base.C_POTION
        for en in self.enemies:
            code[en["y"]][en["x"]] = base.C_BOSS if en.get("boss") else base.C_ENEMY
        code[self.py][self.px] = base.C_PLAYER

        grid_ch = np.array(code, dtype=np.float32) / 7.0
        hp_ch = np.full((map.HEIGHT, map.WIDTH), min(self.hp, 20) / 20.0, dtype=np.float32)
        atk_ch = np.full((map.HEIGHT, map.WIDTH), min(self.atk, 20) / 20.0, dtype=np.float32)
        floor_ch = np.full((map.HEIGHT, map.WIDTH), self.floor / NUM_FLOORS, dtype=np.float32)
        return np.stack([grid_ch, hp_ch, atk_ch, floor_ch], axis=0)
