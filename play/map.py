WIDTH = 11
HEIGHT = 7

WALL = "■"
FLOOR = "."
PLAYER = "@"
EXIT = "E"

def make_map(width, height):
    grid=[]
    for y in range(height):
        row=[]
        for x in range(width):
            if x==0 or x==width-1 or y==0 or y==height-1:
                row.append(WALL)
            else:
                row.append(FLOOR)
        grid.append(row)
    return grid

def place(grid, x, y, symbol):
    grid[y][x]=symbol

def print_map(grid):
    for row in grid:
        print("".join(row))

if __name__ == "__main__":
    game_map = make_map(WIDTH, HEIGHT)
    place(game_map, 1, 1, PLAYER)
    place(game_map, WIDTH - 2, HEIGHT - 2, EXIT)
    print_map(game_map)
