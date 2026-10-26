import map

ENEMY="g"
POTION="+"
WEAPON="/"
#이러한 정의는 나중에 config같은 곳에 묶어서 보관하나?

#딕셔너리 {}중괄호(?)사용하는 놈 ["나":"누나"] 나중에 "나"라는 키를 부르면 "누나"라는 값이 따라온다...가 맞나?
#가족={"나":"누나"}, 이웃={"친구":"친구엄마"}, 단지 주민=[가족, 이웃] 이런식인가?
def make_enemies():
    """적 목록을 만들어 돌려준다."""
    return [
        {"x":5, "y":1, "hp":3},
        {"x":4, "y":4, "hp":3},# 여기는 마지막 단인데 왜 ,를 붙인걸까?
    ]

def make_items():# 이 함수를 쓰면 아래 리턴값을 받는건가?
    return [
        {"x":3, "y":1, "kind":"weapon"},
        {"x":7, "y":3, "kind":"potion"}
    ]

def find_at(entities, x, y):
    """entities(리스트 목록)에서 (x, y)위치에 있는 것을 찾아 돌려준다.
    없으면 None을 돌려준다.(참고록 0과 None은 다른거임 없다는 값이랑 비어있는 값의 차이)"""
    for e in entities:# 전히 for문과 if문은 어렵다. 아무래도 주어지는 재료(값)가 아래에서 올라오다보니 막연해서 그런듯
        if e["x"]==x and e["y"]==y:# x와 y가 동시에 같으면
            return e
    return None

def draw(px, py, hp, atk, enemies, items):
    """현재 상태를 화면에 그린다. (매번 깨끗한 맵을 새로 만들어 그림)"""
    fresh=map.make_map(map.WIDTH, map.HEIGHT)

    # 출구 → 아이템 → 적 → 플레이어 순으로 새 맵 위에 올린다. 순서에는 의미가 있는것인가?
    map.place(fresh, map.WIDTH-2, map.HEIGHT-2, map.EXIT)# 출구
    for it in items:
        symbol=WEAPON if it["kind"]=="weapon" else POTION# else를 if아래 들여쓰기가 아니라 이렇게 쓸 수 있나?
        map.place(fresh, it["x"], it["y"], symbol)
    for en in enemies:
        map.place(fresh, en["x"], en["y"], ENEMY)
    map.place(fresh, px, py, map.PLAYER)

    print("="*map.WIDTH)
    map.print_map(fresh)
    print(f"체력(HP): {hp} 공격력(ATK): {atk} 이동: w/a/s/d, 종료: q")

if __name__ == "__main__":
    px, py = 1, 1
    hp=10
    atk=1# 무기가 없으면 일단 몸으로라도 때워야지

    game_map=map.make_map(map.WIDTH, map.HEIGHT)
    enemies=make_enemies()# 위에서 만든 적 리스트
    items=make_items()# 위에서 만든 아이템 리스트

    ENEMY_DAMAGE=2# 몬스터짱의 공격력

    draw(px, py, hp, atk, enemies, items) # 초기 위치 및 적, 아이템 리스트의 지정된 딕셔너리 위치 값 불러오기

    while True:
        key = input("어디로 갈까요? > ")

        if key=="q":
            print("게임을 종료합니다.")
            break

        nx, ny= px, py
        if key=="w":
            ny=py-1
        elif key=="s":
            ny=py+1
        elif key=="a":
            nx=px-1
        elif key=="d":
            nx=px+1
        else:
            print("w, a, s, d, q 중에서 눌러주세요.")
            continue

        if game_map[ny][nx]==map.WALL:
            print("벽이라 갈 수 없어요!")
            hp=hp-1
            draw(px, py, hp, atk, enemies, items)
            continue

        target=find_at(enemies, nx, ny)
        if target is not None:
            target["hp"]=target["hp"]-atk
            print(f"적을 공격! (적 남은 체력 {target['hp']})")
            if target["hp"]<=0:
                enemies.remove(target)
                px, py = nx, ny
            else:
                hp=hp-ENEMY_DAMAGE
                print(f"적의 반격! (내 체력 {hp})")

        else:
            item=find_at(items, nx, ny)# 아하 아이템이 있으면 적이 있을리가 없으니 적부터 색적하는거구나!
            if item is not None:
                if item["kind"]=="potion":
                    hp=hp+5
                    print("포션을 마셨다! 체력 +5")
                else:# 지금은 아이템이 2개밖에 없으니 포션 아니면 무기!
                    atk=atk+2
                    print("무기를 얻었다! 공격력 +2")
                items.remove(item)
            px, py, = nx, ny# 몬스터나 벽이랑 다르게 아이템은 '획득했다, 먹었다'느낌을 위해 해당 위치로 이동

        if hp<=0:
            print("체력이 다했습니다, 허접이네요.")
            break

        if px==map.WIDTH-2 and py==map.HEIGHT-2:
            draw(px, py, hp, atk, enemies, items)# 몬스터를 안 죽였을수도, 아이템을 안 먹었을수도 있으니
            print("출구에 도착했습니다!")
            break

        draw(px, py, hp, atk, enemies, items)
# 와....모든걸 이해하면서 넘어갈려니 시간도 오래 걸리고 백엔디작업자로 진로를 정한것도 아니니
# 맨처음 선생님이 말씀해준대로 구성이나 요소들을 '알고만' 일단 넘어가고 완성된걸 보면서 배우는게 나은거 같네요.