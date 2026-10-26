# =============================================================================
# game/player3_claude.py   (제가 만든 3주차 예제 — 보고 따라 타이핑하세요)
# 3주차(1단계 이어서): 적과 전투 + 아이템(포션/무기) 추가
#
# 이번에 배우는 것:
#   - 딕셔너리(dictionary) : {"이름": 값} 형태로 여러 정보를 묶어서 보관 (예: 적의 위치+체력)
#   - 리스트 안에 딕셔너리 : 적 여러 마리, 아이템 여러 개를 한 목록으로 관리
#   - 전투 로직           : 적에게 다가가면 공격 → 적도 반격 → HP가 실제로 깎임
#   - 아이템 효과         : 포션(체력 회복), 무기(공격력 증가)
#   - 사망/승리 처리      : HP가 0이면 패배, 출구 도착이면 승리
#
# 실행 방법: 터미널에서   python game/player3_claude.py
#   (이동: w/a/s/d,  종료: q)  각 키를 누르고 Enter
# =============================================================================

import map   # 1주차 map.py 재사용 (벽/바닥/플레이어/출구 및 함수들)

# -----------------------------------------------------------------------------
# [새 글자 설정] 적과 아이템을 나타낼 글자. (map.py의 WALL/FLOOR 등과 별도로 여기서 정의)
# -----------------------------------------------------------------------------
ENEMY = "g"     # 적 (goblin) — 출구 E와 헷갈리지 않게 소문자 g 사용
POTION = "+"    # 포션 (먹으면 체력 회복)
WEAPON = "/"    # 무기 (먹으면 공격력 증가)


# -----------------------------------------------------------------------------
# [딕셔너리] 적 한 마리는 '위치(x, y)'와 '체력(hp)'을 함께 가진다.
#   딕셔너리는 {"키": 값} 형태. enemy["hp"] 처럼 이름으로 값을 꺼낸다.
#   [리스트 안에 딕셔너리] 적이 여러 마리면 리스트로 묶는다.
# -----------------------------------------------------------------------------
def make_enemies():
    """적 목록을 만들어 돌려준다."""
    return [
        {"x": 5, "y": 1, "hp": 3},   # 골렘? 아니 고블린. 체력 3
        {"x": 4, "y": 4, "hp": 3},
    ]

def make_items():
    """아이템 목록을 만들어 돌려준다. kind로 종류를 구분."""
    return [
        {"x": 3, "y": 1, "kind": "weapon"},   # 무기
        {"x": 7, "y": 3, "kind": "potion"},   # 포션
    ]


def find_at(entities, x, y):
    """entities(적 목록 또는 아이템 목록)에서 (x, y) 위치에 있는 것을 찾아 돌려준다.
    없으면 None(아무것도 없음)을 돌려준다."""
    for e in entities:                 # 목록을 하나씩 살펴보며
        if e["x"] == x and e["y"] == y:   # 위치가 같은 것을 찾으면
            return e                   # 그걸 돌려준다
    return None                        # 끝까지 못 찾으면 None


def draw(px, py, hp, atk, enemies, items):
    """현재 상태를 화면에 그린다. (매번 깨끗한 맵을 새로 만들어 그림 — 2주차와 동일)"""
    fresh = map.make_map(map.WIDTH, map.HEIGHT)

    # 출구 → 아이템 → 적 → 플레이어 순으로 새 맵 위에 올린다.
    map.place(fresh, map.WIDTH - 2, map.HEIGHT - 2, map.EXIT)
    for it in items:
        symbol = WEAPON if it["kind"] == "weapon" else POTION
        map.place(fresh, it["x"], it["y"], symbol)
    for en in enemies:
        map.place(fresh, en["x"], en["y"], ENEMY)
    map.place(fresh, px, py, map.PLAYER)

    print("=" * map.WIDTH)
    map.print_map(fresh)
    print(f"체력(HP): {hp}   공격력(ATK): {atk}   이동: w/a/s/d, 종료: q")


if __name__ == "__main__":
    # [상태 변수] 이제 HP가 실제로 쓰인다. 공격력(atk)도 추가.
    px, py = 1, 1
    hp = 10
    atk = 1                       # 기본 공격력 1 (무기를 먹으면 올라간다)

    game_map = map.make_map(map.WIDTH, map.HEIGHT)   # 벽 확인용 맵
    enemies = make_enemies()      # 적 목록
    items = make_items()          # 아이템 목록

    ENEMY_DAMAGE = 2              # 적이 반격할 때 주는 피해

    draw(px, py, hp, atk, enemies, items)   # 시작 화면

    while True:
        key = input("어디로 갈까요? > ")

        if key == "q":
            print("게임을 종료합니다.")
            break

        # 가려는 위치 계산 (2주차와 동일)
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

        # (1) 벽이면 이동 불가 (2주차와 동일)
        if game_map[ny][nx] == map.WALL:
            print("벽이라 갈 수 없어요!")
            draw(px, py, hp, atk, enemies, items)
            continue

        # (2) 가려는 칸에 적이 있으면 → 전투
        target = find_at(enemies, nx, ny)   # 그 자리에 적이 있나?
        if target is not None:
            target["hp"] = target["hp"] - atk        # 내 공격력만큼 적 체력 깎기
            print(f"적을 공격! (적 남은 체력 {target['hp']})")
            if target["hp"] <= 0:
                enemies.remove(target)               # 적 처치 → 목록에서 제거
                px, py = nx, ny                      # 빈 자리로 이동
                print("적을 쓰러뜨렸다!")
            else:
                hp = hp - ENEMY_DAMAGE               # 적이 살아있으면 반격당함
                print(f"적의 반격! (내 체력 {hp})")
                # 적이 살아있으므로 그 칸으로는 못 들어감 (제자리 유지)
        else:
            # (3) 적이 없으면 → 아이템 확인
            item = find_at(items, nx, ny)
            if item is not None:
                if item["kind"] == "potion":
                    hp = hp + 5
                    print("포션을 마셨다! 체력 +5")
                else:  # weapon
                    atk = atk + 2
                    print("무기를 얻었다! 공격력 +2")
                items.remove(item)                   # 먹은 아이템은 사라짐
            # (4) 아이템이든 빈 칸이든, 이동은 실행
            px, py = nx, ny

        # [패배 판정] 체력이 0 이하가 되면 게임 오버
        if hp <= 0:
            print("체력이 다했습니다... 게임 오버")
            break

        # [승리 판정] 출구 도착
        if px == map.WIDTH - 2 and py == map.HEIGHT - 2:
            draw(px, py, hp, atk, enemies, items)
            print("출구에 도착했습니다! (다음 단계: 여러 층 + 보스 — 4주차)")
            break

        draw(px, py, hp, atk, enemies, items)   # 바뀐 상태로 다시 그리기
