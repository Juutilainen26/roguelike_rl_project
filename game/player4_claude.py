# =============================================================================
# game/player4_claude.py   (제가 만든 4주차 예제 — 보고 따라 타이핑하세요)
# 4주차(1단계 완성): 여러 층(floor) + 무작위 맵 + 마지막 층 보스
#
# 이번에 배우는 것:
#   - random 모듈       : 적/아이템을 매번 다른 위치에 무작위로 배치 (로그라이크의 핵심!)
#   - 층(floor) 진행    : 출구에 도착하면 다음 층으로. 층마다 새로 생성.
#   - 보스              : 마지막 층에 강한 적(B). 이걸 처치하면 승리.
#   - dict.get()        : 딕셔너리에서 없을 수도 있는 키를 안전하게 꺼내기 (보스 여부 확인)
#
# 실행 방법: 터미널에서   python game/player4_claude.py
#   (이동: w/a/s/d,  종료: q)
# =============================================================================

import map       # 1주차 map.py 재사용
import random    # [새 도구] 무작위 숫자/선택을 만들어주는 파이썬 기본 모듈

# 글자 설정 (3주차 것 + 보스 추가)
ENEMY = "g"      # 일반 적
BOSS = "B"       # 보스
POTION = "+"     # 포션
WEAPON = "/"     # 무기

NUM_FLOORS = 3          # 총 층 수. 3층이 보스 층.
ENEMY_DAMAGE = 2        # 일반 적의 반격 피해
BOSS_HP = 8             # 보스 체력 (일반 적보다 훨씬 높음)
BOSS_DAMAGE = 3         # 보스의 반격 피해


def random_cell(occupied):
    """비어 있는 칸의 좌표(x, y)를 무작위로 하나 골라 돌려준다.
    occupied: 이미 무언가 놓인 좌표들의 집합(set). 겹치지 않게 피한다."""
    while True:
        # random.randint(a, b) : a 이상 b 이하의 정수를 무작위로 하나 준다.
        x = random.randint(1, map.WIDTH - 2)   # 테두리(0, 끝)는 벽이라 제외
        y = random.randint(1, map.HEIGHT - 2)
        if (x, y) not in occupied:             # 이미 쓴 자리가 아니면
            occupied.add((x, y))               # 썼다고 표시하고
            return x, y                        # 그 좌표를 돌려준다


def make_floor(floor):
    """floor 층에 놓을 적 목록과 아이템 목록을 무작위로 만들어 돌려준다.
    마지막 층이면 보스도 추가한다."""
    # 플레이어 시작칸(1,1)과 출구칸은 미리 '사용중'으로 표시해 피한다.
    occupied = {(1, 1), (map.WIDTH - 2, map.HEIGHT - 2)}

    enemies = []
    items = []

    # 일반 적 2마리를 무작위 위치에
    for i in range(2):
        x, y = random_cell(occupied)
        enemies.append({"x": x, "y": y, "hp": 3})

    # 무기 1개, 포션 1개를 무작위 위치에
    x, y = random_cell(occupied)
    items.append({"x": x, "y": y, "kind": "weapon"})
    x, y = random_cell(occupied)
    items.append({"x": x, "y": y, "kind": "potion"})

    # 마지막 층이면 보스를 추가. 딕셔너리에 "boss": True 표시를 달아 구분.
    if floor == NUM_FLOORS:
        x, y = random_cell(occupied)
        enemies.append({"x": x, "y": y, "hp": BOSS_HP, "boss": True})

    return enemies, items


def find_at(entities, x, y):
    """entities에서 (x, y) 위치에 있는 것을 찾아 돌려준다. 없으면 None."""
    for e in entities:
        if e["x"] == x and e["y"] == y:
            return e
    return None


def draw(floor, px, py, hp, atk, enemies, items):
    """현재 상태를 화면에 그린다."""
    fresh = map.make_map(map.WIDTH, map.HEIGHT)

    map.place(fresh, map.WIDTH - 2, map.HEIGHT - 2, map.EXIT)
    for it in items:
        symbol = WEAPON if it["kind"] == "weapon" else POTION
        map.place(fresh, it["x"], it["y"], symbol)
    for en in enemies:
        # en.get("boss") : "boss" 키가 있으면 그 값(True), 없으면 None.
        # 보스면 B, 일반 적이면 g 로 그린다.
        symbol = BOSS if en.get("boss") else ENEMY
        map.place(fresh, en["x"], en["y"], symbol)
    map.place(fresh, px, py, map.PLAYER)

    print("=" * map.WIDTH)
    map.print_map(fresh)
    print(f"[{floor}층/{NUM_FLOORS}층]  HP: {hp}  ATK: {atk}   이동: w/a/s/d, 종료: q")


if __name__ == "__main__":
    px, py = 1, 1
    hp = 10
    atk = 1
    floor = 1                              # 현재 층. 1층부터 시작.

    game_map = map.make_map(map.WIDTH, map.HEIGHT)
    enemies, items = make_floor(floor)     # 1층 내용물 무작위 생성

    draw(floor, px, py, hp, atk, enemies, items)

    while True:
        key = input("어디로 갈까요? > ")

        if key == "q":
            print("게임을 종료합니다.")
            break

        nx, ny = px, py
        if key == "w":
            ny = py - 1
        elif key == "s":
            ny = py + 1
        elif key == "a":
            nx = px - 1
        elif key == "d":
            nx = px + 1
        else:
            print("w, a, s, d, q 중에서 눌러주세요.")
            continue

        # 벽
        if game_map[ny][nx] == map.WALL:
            print("벽이라 갈 수 없어요!")
            draw(floor, px, py, hp, atk, enemies, items)
            continue

        # 적(보스 포함) 전투
        target = find_at(enemies, nx, ny)
        if target is not None:
            target["hp"] = target["hp"] - atk
            who = "보스" if target.get("boss") else "적"
            print(f"{who}를 공격! (남은 체력 {target['hp']})")
            if target["hp"] <= 0:
                enemies.remove(target)
                px, py = nx, ny
                if target.get("boss"):          # 방금 잡은 게 보스면 → 게임 승리
                    draw(floor, px, py, hp, atk, enemies, items)
                    print("보스를 처치했습니다! 게임 클리어! 🎉")
                    break
                print(f"{who}를 쓰러뜨렸다!")
            else:
                damage = BOSS_DAMAGE if target.get("boss") else ENEMY_DAMAGE
                hp = hp - damage
                print(f"{who}의 반격! (내 체력 {hp})")
        else:
            # 아이템
            item = find_at(items, nx, ny)
            if item is not None:
                if item["kind"] == "potion":
                    hp = hp + 5
                    print("포션을 마셨다! 체력 +5")
                else:
                    atk = atk + 2
                    print("무기를 얻었다! 공격력 +2")
                items.remove(item)
            px, py = nx, ny

        # 패배
        if hp <= 0:
            print("체력이 다했습니다... 게임 오버")
            break

        # 출구 도착 처리
        if px == map.WIDTH - 2 and py == map.HEIGHT - 2:
            if floor < NUM_FLOORS:
                # 아직 보스 층이 아니면 → 다음 층으로 내려간다.
                floor = floor + 1
                px, py = 1, 1                    # 시작 위치로 리셋
                enemies, items = make_floor(floor)   # 새 층 무작위 생성
                print(f"===== {floor}층으로 내려간다! =====")
            else:
                # 보스 층의 출구는 잠겨 있다. 보스를 먼저 잡아야 한다.
                print("보스를 처치하기 전에는 내려갈 수 없다!")

        draw(floor, px, py, hp, atk, enemies, items)
