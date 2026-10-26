WIDTH = 11 # 맵의 가로 칸 수
HEIGHT = 7 # 맵의 세로 칸 수

# 오브젝트 모양 설정
WALL = "■"
FLOOR = "."
PLAYER = "@"
EXIT = "E"

# def 이름(재료) : 레시피 이름, 필요할때 재료를 준비하고 레시피를 부르면 알아서 조합해준다.
def make_map(width, height):
    """가로 width, 세로 height 크기의 맵을 만들어서 돌려준다.
    맵은 '리스트 안에 리스트' (2차원 리스트)로 표현한다."""
    # 리스트:여러 값을 순서대로 담는 상자. 대괄호[]로 만든다.
    # grid는 한 줄 들을 담는 바깥 리스트다.
    grid=[]
    
    # for문 : 정해진 횟수만큼 같은 작업을 반복한다.
    for y in range(height):
        row=[]
        for x in range(width):
            # if문 : 상황에 따라 다른 값을 고른다.
            if x==0 or x==width-1 or y==0 or y==height-1:
                row.append(WALL)
            else:
                row.append(FLOOR)
        grid.append(row)
    return grid

def place(grid, x, y, symbol):
    """맵의 (x, y) 위치에 원하는 글자(symbol)를 놓는다."""
    # grid[y][x] : y번째 줄의 x번째 칸.
    # 순서 주의! 세로(y)가 먼저, 가로(x)가 나중이다.
    # 2차원 리스트, 열(y) 선택후 행(x)을 선택해야한다. 다중 차원의 빗장열기 머리속에 넣어놓자.
    grid[y][x]=symbol

def print_map(grid):
    """맵(2차원 리스트)을 화면에 글자로 출력한다."""
    # 2차원 리스트라서 한곁 벗겨내고 한줄짜리 리스트가 row에 입력된다.
    for row in grid:
        print("".join(row)) # ""의 의미는 간격사이에 아무것도 두지 말라

if __name__ == "__main__":# map파일인데 map이름으로 실행할때만 이걸 활성화 해라
    game_map = make_map(WIDTH, HEIGHT)

    place(game_map, 1, 1, PLAYER)
    place(game_map, WIDTH - 2, HEIGHT - 2, EXIT)

    print_map(game_map)