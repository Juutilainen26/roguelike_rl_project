import map
import random

ENEMY="g"
BOSS="B"
POTION="+"
WEAPON="/"

NUM_FLOORS=3# 3층 명시
ENEMY_DAMAGE=2
BOSS_HP=8
BOSS_DAMAGE=3

def random_cell(occupide):
    """비어 있는 칸의 좌표(x, y)를 무작위로 하나 골라 돌려준다.
    occupied: 이미 무언가 놓인 좌표들의 집합(set). 겹치지 않게 피한다."""
    while True:
        x=random.randint(1, map.WIDTH-2)# -2는 벽이 아니라 바닥도 한칸 포함아닌가?10이 벽이고 9가 바닥인데 (1,9)면 1~8사이의 값아 닌가?
        y=random.randint(1, map.HEIGHT-2)
        if (x, y) not in occupide:#occupide안에 없다면
            occupide.add((x,y))#그 x, y를 더한다. 무슨말이지?
            return x, y# 안쓴 좌표를 쓰라고 반환하는건가?
        
def make_floor(floor):
    occupied={(1, 1), (map.WIDTH-2, map.HEIGHT-2)}

    enemies=[]
    items=[]

    for i in range(2):
        x, y= random_cell(occupied)
        enemies.append({"x":x, "y":y, "hp":3})

    x, y=random_cell(occupied)
    items.append({"x":x, "y":y, "kind":"weapon"})
    x, y=random_cell(occupied)
    items.append({"x":x, "y":y, "kind":"potion"})

    if floor==NUM_FLOORS:
        x,y = random_cell(occupied)
        enemies.append({"x":x, "y":y, "hp":BOSS_HP, "boss":True})
    
    return enemies, items

def find_at(entities, x, y):
    for e in entities:
        if e["x"]==x and e["y"]==y:
            return e
    return None

def draw(floor, px, py, hp, atk, enemies, items):
    fresh=map.make_map(map.WIDTH, map.HEIGHT)

    map.place(fresh, map.WIDTH-2, map.HEIGHT-2, map.EXIT)
    for it in items:
        symbol=WEAPON if it["kind"] == "weapon" else POTION
        map.place(fresh, it["x"], it["y"], symbol)
    for en in enemies:
        # boss 키값이 일단 있으니깐 트루가 반환되긴 하는데 어째서 없으면 논이 되는거지?
        symbol=BOSS if en.get("boss") else ENEMY
        map.place(fresh, en["x"], en["y"], symbol)
    map.place(fresh, px, py, map.PLAYER)

    print("="*map.WIDTH)
    map.print_map(fresh)
    print(f"[{floor}층/{NUM_FLOORS}층] HP: {hp}  ATK: {atk}    이동 w/a/s/d, 종료: q")

if __name__=="__main__":
    px, py = 1, 1
    hp = 10
    atk = 1
    floor = 1

    game_map=map.make_map(map.WIDTH, map.HEIGHT)
    enemies, items=make_floor(floor)

    draw(floor, px, py, hp, atk, enemies, items)

    while True:
        key = input("어디로 갈까요? > ")

        if key =="q":
            print("게임을 종료합니다.")
            break

        nx, ny = px, py
        if key == "w":
            ny = py - 1
        elif key == "s":
            ny = py + 1
        elif key == "a":
            nx = px -1
        elif key == "d":
            nx = px + 1
        else:
            print("w, s, a, d, q 중에서 눌러주세요.")
            continue

        if game_map[ny][nx]==map.WALL:
            print("벽이라 갈 수 없어요!")
            draw(floor, px, py, hp, atk, enemies, items)
            hp = hp-1
            continue

        target=find_at(enemies, nx, ny)
        if target is not None:
            target["hp"]=target["hp"] - atk
            who="보스" if target.get("boss") else "적"
            print(f"{who}를 공격! (남은 체력 {target['hp']})")
            if target["hp"] <=0:
                enemies.remove(target)
                px, py = nx, ny
                if target.get("boss"):
                    draw(floor, px, py, hp, atk, enemies, items)
                    print("보스를 처지했습니다! 아직이에요! 좀더!")
                    break
                print(f"{who}를 쓰러트렸다!")
            else:
                damage=BOSS_DAMAGE if target.get("boss") else ENEMY_DAMAGE
                hp=hp-damage
                print(f"{who}의 반격! (내 체력 {hp})")
        else:
            item = find_at(items, nx, ny)
            if item is not None:
                if item["kind"] == "potion":
                    hp = hp+5
                    print("포션을 마셨다! 체력 +5")
                else:
                    atk = atk+2
                    print("무기를 얻었다! 공격력 +2")
                items.remove(item)
            px, py= nx, ny

        if hp <=0:
            print("체력이 다 했습니다.... 게임 못하네")
            break

        if px==map.WIDTH-2 and py == map.HEIGHT-2:
            if floor < NUM_FLOORS:
                floor=floor+1
                px, py=1,1
                enemies, items=make_floor(floor)
                print(f"===== {floor}층으로 내려간다! =====")
            else:
                print("넌 못 지나간다!")
        
        draw(floor, px, py, hp, atk, enemies, items)