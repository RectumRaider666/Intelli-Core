from PIL import Image, ImageDraw
import random

CELL_SIZE = 20
WALL = 2
WIDTH = 1000
HEIGHT = 1000

DIRS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0)
}

OPPOSITE = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E"
}

class Cell:
    def __init__(self):
        self.walls = {"N": True, "S": True, "E": True, "W": True}
        self.visited = False

def gen_grid(w, h):
    return [[Cell() for _ in range(h)] for _ in range(w)]

def neighbors(x, y, grid):
    for direction, (dx, dy) in DIRS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            yield direction, nx, ny

def carve_maze(grid, start_x=0, start_y=0):
    stack = [(start_x, start_y)]
    grid[start_x][start_y].visited = True
    while stack:
        x, y = stack[-1]
        unvisited = []
        for direction, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                if not grid[nx][ny].visited:
                    unvisited.append((direction, nx, ny))
        if not unvisited:
            stack.pop()
            continue
        direction, nx, ny = random.choice(unvisited)
        grid[x][y].walls[direction] = False
        grid[nx][ny].walls[OPPOSITE[direction]] = False
        grid[nx][ny].visited = True
        stack.append((nx, ny))

def add_entry_exit(grid):
    grid[0][0].walls["W"] = False
    grid[WIDTH-1][HEIGHT-1].walls["E"] = False

def draw_maze(grid, filename:str):
    img_w = WIDTH * CELL_SIZE + WALL
    img_h = HEIGHT * CELL_SIZE + WALL
    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            cell = grid[x][y]
            x1 = x * CELL_SIZE
            y1 = y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            if cell.walls["N"]:
                draw.line((x1, y1, x2, y1), fill="black", width=WALL)
            if cell.walls["S"]:
                draw.line((x1, y2, x2, y2), fill="black", width=WALL)
            if cell.walls["E"]:
                draw.line((x2, y1, x2, y2), fill="black", width=WALL)
            if cell.walls["W"]:
                draw.line((x1, y1, x1, y2), fill="black", width=WALL)
    img.save(filename)
    print(f"Maze saved as {filename}")

grid = gen_grid(WIDTH, HEIGHT)
carve_maze(grid)
add_entry_exit(grid)
draw_maze(grid, filename=str(f"mazes/{HEIGHT}X{WIDTH}-{CELL_SIZE}:maze.png"))
